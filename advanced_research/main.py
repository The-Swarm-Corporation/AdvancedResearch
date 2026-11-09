"""AdvancedResearch: the orchestrator-worker research pattern from
Anthropic's "How we built our multi-agent research system", built on the
Swarms API (https://api.swarms.world) for every agent and Exa
(https://exa.ai) for web search.

One research run:
1. The lead researcher plans the query and writes one subtask per search
   subagent, scaling the number of subagents to the query's complexity.
2. The subagents run in parallel. Each searches Exa, reads the results,
   records cited findings and asks for narrower follow-up searches until
   its objective is covered or its search rounds run out.
3. The lead researcher writes the report from the findings and decides
   whether gaps need another research round (up to ``max_loops``).
4. The citation agent checks every claim against the numbered source
   list, and the references section is built from the sources actually
   cited.

Every agent is a single call to ``/v1/agent/completions`` and every search
is a single call to Exa's ``/search``, so no agent framework or model
provider SDK is needed.
"""

import concurrent.futures
import json
import os
import re
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx
import orjson
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field

from advanced_research.prompts import (
    get_citation_prompt,
    get_orchestrator_prompt,
    get_subagent_prompt,
    get_synthesis_prompt,
)

load_dotenv()

SWARMS_BASE_URL = os.getenv(
    "SWARMS_BASE_URL", "https://api.swarms.world"
).rstrip("/")
EXA_BASE_URL = os.getenv("EXA_BASE_URL", "https://api.exa.ai").rstrip(
    "/"
)

DEFAULT_WORKER_MODEL_NAME = "gpt-5.4-mini"
DEFAULT_WORKER_MAX_TOKENS = 3000
DEFAULT_DIRECTOR_MODEL_NAME = "gpt-5.5"
DEFAULT_DIRECTOR_MAX_TOKENS = 4000
DEFAULT_EXA_SEARCH_NUM_RESULTS = 5
DEFAULT_EXA_SEARCH_MAX_CHARACTERS = 1500

# The API gateway in front of api.swarms.world ends a request at 30 s.
GATEWAY_TIMEOUT_SECONDS = 29.0

OUTPUT_TYPES = [
    "final",
    "last",
    "all",
    "str",
    "string",
    "list",
    "dict",
    "json",
    "markdown",
]


def generate_id() -> str:
    """Return a unique id for a research session."""
    return f"AdvancedResearch-{uuid.uuid4()}-time-{datetime.now().strftime('%Y%m%d%H%M%S')}"


class AdvancedResearchAdditionalConfig(BaseModel):
    """Settings for the search subagents."""

    worker_model_name: str = Field(
        default=DEFAULT_WORKER_MODEL_NAME,
        description="The Swarms API model the search subagents use.",
    )
    worker_max_tokens: int = Field(
        default=DEFAULT_WORKER_MAX_TOKENS,
        description="The maximum number of output tokens for each subagent call.",
    )
    exa_search_num_results: int = Field(
        default=DEFAULT_EXA_SEARCH_NUM_RESULTS,
        description="The number of results each Exa search returns.",
    )
    exa_search_max_characters: int = Field(
        default=DEFAULT_EXA_SEARCH_MAX_CHARACTERS,
        description="The maximum number of page-text characters kept per Exa result.",
    )
    worker_search_rounds: int = Field(
        default=2,
        ge=1,
        description="Rounds of search a subagent may run: the planned queries, then follow-ups it asks for.",
    )
    max_subagents: int = Field(
        default=5,
        ge=1,
        description="The most subagents the lead researcher may start in one research round.",
    )


schema = AdvancedResearchAdditionalConfig()


class ResearchAPIError(RuntimeError):
    """A Swarms API or Exa request failed."""


def _post_json(
    service: str,
    url: str,
    headers: Dict[str, str],
    body: Dict[str, Any],
    timeout: float = 120.0,
    attempts: int = 3,
) -> Dict[str, Any]:
    """POST a JSON body and return the JSON response.

    Retries connection errors, 429s and short-lived 5xx responses. A 503
    or 504 that arrives after about 30 seconds is the Swarms API gateway
    limit, and a retry would only run the same slow call again, so it
    raises straight away with advice instead.
    """
    for attempt in range(1, attempts + 1):
        started = time.monotonic()
        try:
            response = httpx.post(
                url, headers=headers, json=body, timeout=timeout
            )
        except httpx.TransportError as error:
            if attempt == attempts:
                raise ResearchAPIError(
                    f"{service} request failed: {error}"
                ) from error
            time.sleep(2**attempt)
            continue

        elapsed = time.monotonic() - started
        status = response.status_code
        if (
            status in (503, 504)
            and elapsed >= GATEWAY_TIMEOUT_SECONDS
        ):
            raise ResearchAPIError(
                f"{service} returned {status} after {elapsed:.0f} s, the "
                "Swarms API's 30-second request limit. Use a faster model "
                "or a lower max_tokens for this agent."
            )
        if status in (429, 500, 502, 503) and attempt < attempts:
            time.sleep(2**attempt)
            continue
        if status >= 400:
            raise ResearchAPIError(
                f"{service} returned {status}: {response.text[:500]}"
            )
        return response.json()
    raise ResearchAPIError(f"{service} request failed")


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ResearchAPIError(
            f"{name} is not set. Add it to your environment or .env file."
        )
    return value


def swarms_agent(
    agent_name: str,
    system_prompt: str,
    task: str,
    model_name: str = DEFAULT_WORKER_MODEL_NAME,
    max_tokens: int = DEFAULT_WORKER_MAX_TOKENS,
    img: Optional[str] = None,
    max_loops: int = 1,
) -> Tuple[str, float]:
    """Run one agent on the Swarms API.

    Args:
        agent_name: Name of the agent; its replies are read back by name.
        system_prompt: The agent's system prompt.
        task: The task for this call.
        model_name: Any model listed by GET /v1/models/available.
        max_tokens: Maximum output tokens.
        img: Optional https:// image URL or base64 image.
        max_loops: Agent loops for this call.

    Returns:
        The agent's reply text and the call's cost in USD.
    """
    body: Dict[str, Any] = {
        "agent_config": {
            "agent_name": agent_name,
            "system_prompt": system_prompt,
            "model_name": model_name,
            "max_loops": max_loops,
            "max_tokens": max_tokens,
        },
        "task": task,
    }
    if img:
        body["img"] = img
    data = _post_json(
        "Swarms API",
        f"{SWARMS_BASE_URL}/v1/agent/completions",
        {
            "x-api-key": _require_env("SWARMS_API_KEY"),
            "Content-Type": "application/json",
        },
        body,
    )
    outputs = data.get("outputs") or []
    if isinstance(outputs, str):
        text = outputs
    else:
        replies = [
            message["content"]
            for message in outputs
            if isinstance(message, dict)
            and message.get("role") == agent_name
            and isinstance(message.get("content"), str)
        ]
        text = "\n".join(replies)
    cost = float((data.get("usage") or {}).get("total_cost") or 0.0)
    return text.strip(), cost


def exa_search(
    query: str,
    num_results: int = DEFAULT_EXA_SEARCH_NUM_RESULTS,
    max_characters: int = DEFAULT_EXA_SEARCH_MAX_CHARACTERS,
) -> List[Dict[str, Any]]:
    """Search the web with Exa and return the results with page text.

    Args:
        query: The search query.
        num_results: Number of results to return.
        max_characters: Page-text characters to keep per result.

    Returns:
        A list of dicts with url, title, published_date, text and
        highlights.
    """
    data = _post_json(
        "Exa",
        f"{EXA_BASE_URL}/search",
        {
            "x-api-key": _require_env("EXA_API_KEY"),
            "Content-Type": "application/json",
        },
        {
            "query": query,
            "numResults": num_results,
            "type": "auto",
            "contents": {
                "text": {"maxCharacters": max_characters},
                "highlights": {
                    "numSentences": 3,
                    "highlightsPerUrl": 2,
                },
            },
        },
        timeout=60.0,
    )
    return [
        {
            "url": result.get("url", ""),
            "title": result.get("title") or "",
            "published_date": (result.get("publishedDate") or "")[
                :10
            ],
            "text": result.get("text") or "",
            "highlights": result.get("highlights") or [],
        }
        for result in data.get("results", [])
        if result.get("url")
    ]


class SourceRegistry:
    """Numbers every source found during a run, shared by all subagents,
    so a citation like [3] means the same page everywhere."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._ids: Dict[str, int] = {}
        self.sources: List[Dict[str, Any]] = []

    def add(self, result: Dict[str, Any]) -> int:
        """Register a search result and return its citation number."""
        with self._lock:
            url = result["url"]
            if url not in self._ids:
                self.sources.append(result)
                self._ids[url] = len(self.sources)
            return self._ids[url]

    def get(self, number: int) -> Optional[Dict[str, Any]]:
        if 1 <= number <= len(self.sources):
            return self.sources[number - 1]
        return None

    def format(self, numbers: List[int]) -> str:
        """Render the given sources as numbered evidence for a prompt."""
        blocks = []
        for number in numbers:
            source = self.get(number)
            if source is None:
                continue
            date = (
                f" ({source['published_date']})"
                if source["published_date"]
                else ""
            )
            highlights = " ".join(source["highlights"])
            blocks.append(
                f"[{number}] {source['title']}{date}\n"
                f"URL: {source['url']}\n"
                f"Highlights: {highlights}\n"
                f"Text: {source['text']}"
            )
        return "\n\n".join(blocks)


def _parse_json(text: str) -> Optional[Any]:
    """Parse the JSON object in a model reply, with or without code
    fences or surrounding prose."""
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    candidates = [fenced.group(1)] if fenced else []
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


def _today() -> str:
    return datetime.now().strftime("%d %B %Y")


def _subtask_text(subtask: Dict[str, Any]) -> str:
    lines = [
        f"Today's date: {_today()}",
        f"Objective: {subtask['objective']}",
    ]
    if subtask.get("output_format"):
        lines.append(f"Return: {subtask['output_format']}")
    if subtask.get("boundaries"):
        lines.append(f"Out of scope: {subtask['boundaries']}")
    return "\n".join(lines)


def _normalize_subtask(
    subtask: Union[str, Dict[str, Any]],
) -> Dict[str, Any]:
    if isinstance(subtask, str):
        return {"objective": subtask, "search_queries": [subtask]}
    objective = str(subtask.get("objective") or "").strip()
    queries = [
        str(query).strip()
        for query in subtask.get("search_queries") or []
        if str(query).strip()
    ] or [objective]
    return {
        **subtask,
        "objective": objective,
        "search_queries": queries,
    }


def run_agent(
    i: int,
    query: Union[str, Dict[str, Any]],
    registry: Optional[SourceRegistry] = None,
    config: AdvancedResearchAdditionalConfig = schema,
) -> Dict[str, Any]:
    """Run one search subagent on its subtask.

    Each round searches Exa for the round's queries in parallel, registers
    the results as numbered sources, and asks the subagent to record cited
    findings. The subagent can ask for narrower follow-up searches, which
    run in the next round, until its objective is covered or
    ``config.worker_search_rounds`` is reached.

    Args:
        i: Index of the subagent, used in its name.
        query: A research question, or a subtask dict with objective,
            search_queries, output_format and boundaries.
        registry: The run's shared source list. A new one is used if None.
        config: Subagent settings.

    Returns:
        A dict with the subagent's objective, findings, key_facts,
        conflicts, the source numbers it was given, its confidence and its
        cost in USD.
    """
    registry = registry or SourceRegistry()
    subtask = _normalize_subtask(query)
    agent_name = f"Worker-Search-Agent-{i}"
    queries = subtask["search_queries"][:3]
    seen_queries: List[str] = []
    source_numbers: List[int] = []
    findings: Dict[str, Any] = {}
    cost = 0.0

    for round_number in range(1, config.worker_search_rounds + 1):
        queries = [q for q in queries if q not in seen_queries][:3]
        if not queries:
            break
        seen_queries.extend(queries)
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(queries)
        ) as pool:
            batches = list(
                pool.map(
                    lambda q: exa_search(
                        q,
                        config.exa_search_num_results,
                        config.exa_search_max_characters,
                    ),
                    queries,
                )
            )
        for results in batches:
            for result in results:
                number = registry.add(result)
                if number not in source_numbers:
                    source_numbers.append(number)

        previous = (
            f"\n\nYour findings from the previous round:\n{json.dumps(findings, ensure_ascii=False)}"
            if findings
            else ""
        )
        task = (
            f"{_subtask_text(subtask)}\n\n"
            f"Search round {round_number} of {config.worker_search_rounds}. "
            f"Searches run so far: {json.dumps(seen_queries, ensure_ascii=False)}"
            f"{previous}\n\n"
            f"Search results:\n\n{registry.format(source_numbers) or 'No results were found.'}"
        )
        text, call_cost = swarms_agent(
            agent_name=agent_name,
            system_prompt=get_subagent_prompt(
                "breadth_first", config.worker_search_rounds
            ),
            task=task,
            model_name=config.worker_model_name,
            max_tokens=config.worker_max_tokens,
        )
        cost += call_cost
        parsed = _parse_json(text)
        findings = (
            parsed
            if isinstance(parsed, dict)
            else {"findings": text, "follow_up_queries": []}
        )
        queries = [
            str(q).strip()
            for q in findings.get("follow_up_queries") or []
            if str(q).strip()
        ]
        if findings.get("coverage_assessment") == "comprehensive":
            break

    logger.info(
        f"{agent_name} finished with {len(source_numbers)} sources"
    )
    return {
        "agent_name": agent_name,
        "objective": subtask["objective"],
        "findings": findings.get("findings", ""),
        "key_facts": findings.get("key_facts") or [],
        "conflicts": findings.get("conflicts") or "",
        "source_numbers": source_numbers,
        "searches": seen_queries,
        "confidence_level": findings.get("confidence_level"),
        "coverage_assessment": findings.get("coverage_assessment"),
        "cost": cost,
    }


def run_worker_agents(
    subtasks: List[Union[str, Dict[str, Any]]],
    registry: Optional[SourceRegistry] = None,
    config: AdvancedResearchAdditionalConfig = schema,
) -> List[Dict[str, Any]]:
    """Run one search subagent per subtask, all in parallel, and return
    their results in subtask order. A subagent that fails is reported in
    its result instead of failing the whole round."""
    registry = registry or SourceRegistry()

    def run(item: Tuple[int, Union[str, Dict[str, Any]]]):
        index, subtask = item
        try:
            return run_agent(index, subtask, registry, config)
        except ResearchAPIError as error:
            logger.warning(f"Subagent {index} failed: {error}")
            return {
                "agent_name": f"Worker-Search-Agent-{index}",
                "objective": _normalize_subtask(subtask)["objective"],
                "findings": "",
                "key_facts": [],
                "conflicts": "",
                "source_numbers": [],
                "searches": [],
                "error": str(error),
                "cost": 0.0,
            }

    if not subtasks:
        return []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(len(subtasks), config.max_subagents)
    ) as pool:
        return list(pool.map(run, enumerate(subtasks, start=1)))


def execute_worker_search_agents(queries: List[str]) -> str:
    """Research each query with its own search subagent, in parallel, and
    return their findings as one string.

    Args:
        queries: Research questions, one per subagent.

    Returns:
        The subagents' findings joined with blank lines.
    """
    results = run_worker_agents(queries)
    return "\n\n".join(
        f"{r['objective']}\n{r['findings']}" for r in results
    )


def create_director_agent(
    agent_name: str = "Director-Agent",
    model_name: str = DEFAULT_DIRECTOR_MODEL_NAME,
    task: Optional[str] = None,
    img: Optional[str] = None,
    max_loops: int = 1,
    max_tokens: int = DEFAULT_DIRECTOR_MAX_TOKENS,
    max_subagents: int = schema.max_subagents,
) -> Tuple[Dict[str, Any], float]:
    """Run the lead researcher's planning step.

    Args:
        agent_name: Name of the lead researcher.
        model_name: Swarms API model for the lead researcher.
        task: The research query, plus any earlier report and gaps.
        img: Optional https:// image URL or base64 image.
        max_loops: Agent loops for the call.
        max_tokens: Maximum output tokens.
        max_subagents: Upper bound on subtasks.

    Returns:
        The research plan (complexity, strategy and subtasks) and the
        call's cost in USD.
    """
    text, cost = swarms_agent(
        agent_name=agent_name,
        system_prompt=get_orchestrator_prompt(max_subagents),
        task=task or "",
        model_name=model_name,
        max_tokens=max_tokens,
        img=img,
        max_loops=max_loops,
    )
    plan = _parse_json(text)
    if not isinstance(plan, dict) or not plan.get("subtasks"):
        logger.warning(
            "The lead researcher returned no usable plan; researching the query as one subtask."
        )
        plan = {
            "complexity": "simple",
            "strategy": "Research the query directly.",
            "subtasks": [{"objective": task or ""}],
        }
    plan["subtasks"] = [
        _normalize_subtask(subtask)
        for subtask in plan["subtasks"][:max_subagents]
        if isinstance(subtask, (str, dict))
    ]
    return plan, cost


def _split_report(text: str) -> Tuple[str, bool, List[str]]:
    """Split the synthesis reply into the report and its trailing
    needs_more_research decision."""
    blocks = list(
        re.finditer(
            r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL
        )
    )
    if not blocks:
        return text.strip(), False, []
    last = blocks[-1]
    try:
        decision = json.loads(last.group(1))
    except json.JSONDecodeError:
        return text.strip(), False, []
    report = (text[: last.start()] + text[last.end() :]).strip()
    gaps = [
        str(g) for g in decision.get("gaps") or [] if str(g).strip()
    ]
    return report, bool(decision.get("needs_more_research")), gaps


def _cited_numbers(report: str) -> List[int]:
    numbers: List[int] = []
    for match in re.finditer(r"\[(\d+)\]", report):
        number = int(match.group(1))
        if number not in numbers:
            numbers.append(number)
    return numbers


def build_references(report: str, registry: SourceRegistry) -> str:
    """Return a Markdown references list for the sources the report
    cites, in citation-number order. Unknown numbers are left out."""
    lines = []
    for number in sorted(_cited_numbers(report)):
        source = registry.get(number)
        if source is None:
            continue
        title = source["title"] or source["url"]
        date = (
            f", {source['published_date']}"
            if source["published_date"]
            else ""
        )
        lines.append(f"[{number}] {title}{date}. {source['url']}")
    return "\n".join(lines)


class Conversation:
    """The run's message history: the query, the plan, each subagent's
    findings and each report."""

    def __init__(self, name: str = "conversation") -> None:
        self.name = name
        self.messages: List[Dict[str, Any]] = []

    def add(self, role: str, content: Any) -> None:
        self.messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_final_message(self) -> Optional[Any]:
        return self.messages[-1]["content"] if self.messages else None

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self.messages)

    def format(self, output_type: str) -> Any:
        """Return the history in one of OUTPUT_TYPES."""
        if output_type in ("final", "last"):
            return self.get_final_message()
        if output_type in ("list", "dict"):
            return self.get_history()
        if output_type == "json":
            return json.dumps(
                self.get_history(), indent=2, ensure_ascii=False
            )

        def text(content: Any) -> str:
            return (
                content
                if isinstance(content, str)
                else json.dumps(content, indent=2, ensure_ascii=False)
            )

        if output_type == "markdown":
            return "\n\n".join(
                f"### {m['role']}\n\n{text(m['content'])}"
                for m in self.messages
            )
        return "\n\n".join(
            f"{m['role']}: {text(m['content'])}"
            for m in self.messages
        )


def create_json_file(data: dict, file_name: str) -> None:
    """Write data to a JSON file, merging it into the file's existing
    object if there is one."""
    data_to_write = data
    if os.path.exists(file_name):
        try:
            with open(file_name, "rb") as f:
                existing_data = orjson.loads(f.read())
        except Exception:
            existing_data = {}
        if isinstance(existing_data, dict):
            existing_data.update(data)
            data_to_write = existing_data

    with open(file_name, "wb") as f:
        f.write(
            orjson.dumps(data_to_write, option=orjson.OPT_INDENT_2)
        )


class AdvancedResearch:
    """Multi-agent web research on the Swarms API and Exa.

    Attributes:
        id: Unique identifier for the research session.
        name: Name of the research system.
        description: Description of the research system.
        worker_model_name: Swarms API model for the search subagents.
        worker_max_tokens: Maximum output tokens per subagent call.
        director_agent_name: Name of the lead researcher.
        director_model_name: Swarms API model for the lead researcher,
            the report and the citation pass.
        director_max_tokens: Maximum output tokens for those calls.
        output_type: How run() returns the result; see OUTPUT_TYPES.
        max_loops: Most research rounds; the lead researcher stops early
            when the report has no gaps worth another round.
        export_on: Save the session to examples/outputs/<id>.json.
        director_max_loops: Agent loops for each lead researcher call.
        config: Subagent and search settings.
        conversation: The session's message history.
        sources: The registry of every source found.
        total_cost: Swarms API cost of the session in USD.
    """

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "Advanced Research",
        description: str = "Advanced Research",
        worker_model_name: str = DEFAULT_WORKER_MODEL_NAME,
        director_agent_name: str = "Director-Agent",
        director_model_name: str = DEFAULT_DIRECTOR_MODEL_NAME,
        director_max_tokens: int = DEFAULT_DIRECTOR_MAX_TOKENS,
        output_type: str = "final",
        max_loops: int = 1,
        export_on: bool = False,
        director_max_loops: int = 1,
        worker_max_tokens: int = DEFAULT_WORKER_MAX_TOKENS,
        config: Optional[AdvancedResearchAdditionalConfig] = None,
    ):
        if output_type not in OUTPUT_TYPES:
            raise ValueError(
                f"output_type must be one of {OUTPUT_TYPES}, got {output_type!r}"
            )
        self.id = id or generate_id()
        self.name = name
        self.description = description
        self.worker_model_name = worker_model_name
        self.worker_max_tokens = worker_max_tokens
        self.director_agent_name = director_agent_name
        self.director_model_name = director_model_name
        self.director_max_tokens = director_max_tokens
        self.output_type = output_type
        self.max_loops = max_loops
        self.export_on = export_on
        self.director_max_loops = director_max_loops
        self.config = (config or schema).model_copy(
            update={
                "worker_model_name": worker_model_name,
                "worker_max_tokens": worker_max_tokens,
            }
        )
        self._reset()

    def _reset(self) -> None:
        self.conversation = Conversation(
            name=f"conversation-{self.id}"
        )
        self.sources = SourceRegistry()
        self.worker_results: List[Dict[str, Any]] = []
        self.total_cost = 0.0

    def _director(
        self, system_prompt: str, task: str, max_tokens: int
    ) -> str:
        text, cost = swarms_agent(
            agent_name=self.director_agent_name,
            system_prompt=system_prompt,
            task=task,
            model_name=self.director_model_name,
            max_tokens=max_tokens,
            max_loops=self.director_max_loops,
        )
        self.total_cost += cost
        return text

    def _plan(
        self,
        task: str,
        report: Optional[str],
        gaps: List[str],
        img: Optional[str],
    ) -> Dict[str, Any]:
        planning_task = (
            f"Today's date: {_today()}\nResearch query: {task}"
        )
        if report:
            planning_task += (
                f"\n\nPrevious report:\n{report}\n\nGaps to research:\n"
                + "\n".join(f"- {gap}" for gap in gaps)
            )
        plan, cost = create_director_agent(
            agent_name=self.director_agent_name,
            model_name=self.director_model_name,
            task=planning_task,
            img=img,
            max_loops=self.director_max_loops,
            max_tokens=min(self.director_max_tokens, 2000),
            max_subagents=self.config.max_subagents,
        )
        self.total_cost += cost
        return plan

    def _synthesize(
        self, task: str, previous_report: Optional[str]
    ) -> Tuple[str, bool, List[str]]:
        findings = []
        for result in self.worker_results:
            if result.get("error"):
                findings.append(
                    f"## {result['objective']}\nThis subagent failed: {result['error']}"
                )
                continue
            facts = "\n".join(f"- {f}" for f in result["key_facts"])
            conflicts = (
                f"\nConflicts: {result['conflicts']}"
                if result["conflicts"]
                else ""
            )
            findings.append(
                f"## {result['objective']}\n{result['findings']}\n{facts}{conflicts}"
            )
        previous = (
            f"\n\nYour previous report, to extend rather than repeat:\n{previous_report}"
            if previous_report
            else ""
        )
        text = self._director(
            get_synthesis_prompt(),
            f"Today's date: {_today()}\nOriginal query: {task}{previous}\n\nSubagent findings:\n\n"
            + "\n\n".join(findings),
            self.director_max_tokens,
        )
        return _split_report(text)

    def _cite(self, report: str) -> str:
        # Only the sources the report or the findings cite, so the prompt stays small.
        cited_text = report + "".join(
            result["findings"] + " ".join(result["key_facts"])
            for result in self.worker_results
        )
        numbers = [
            n
            for n in sorted(_cited_numbers(cited_text))
            if self.sources.get(n)
        ]
        if not numbers:
            return report
        try:
            cited = self._director(
                get_citation_prompt(),
                f"Report:\n\n{report}\n\nSource list:\n\n{self.sources.format(numbers)}",
                self.director_max_tokens,
            )
        except ResearchAPIError as error:
            logger.warning(
                f"Citation pass failed, keeping the synthesis citations: {error}"
            )
            cited = report
        return cited.strip() or report

    def step(
        self,
        task: Optional[str],
        img: Optional[str] = None,
        previous_report: Optional[str] = None,
        gaps: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Run one research round: plan, search in parallel, write the
        report.

        Args:
            task: The research query.
            img: Optional https:// image URL or base64 image for planning.
            previous_report: The report from the previous round, if any.
            gaps: Gaps the previous round asked to research.

        Returns:
            A dict with the plan, the report, needs_more_research and gaps.
        """
        plan = self._plan(task, previous_report, gaps or [], img)
        self.conversation.add(self.director_agent_name, plan)

        results = run_worker_agents(
            plan["subtasks"], self.sources, self.config
        )
        for result in results:
            self.total_cost += result["cost"]
            self.conversation.add(
                result["agent_name"],
                {
                    key: result[key]
                    for key in (
                        "objective",
                        "findings",
                        "key_facts",
                        "conflicts",
                        "searches",
                        "error",
                    )
                    if result.get(key)
                },
            )
        self.worker_results.extend(results)

        report, needs_more, new_gaps = self._synthesize(
            task, previous_report
        )
        return {
            "plan": plan,
            "report": report,
            "needs_more_research": needs_more,
            "gaps": new_gaps,
        }

    def run(
        self,
        task: Optional[str] = None,
        img: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Research the task and return the cited report.

        Runs up to max_loops research rounds. After each round the lead
        researcher decides whether gaps need another round. The final
        report then goes through the citation pass and gets a references
        section built from the sources it cites.

        Args:
            task: The research query.
            img: Optional https:// image URL or base64 image.

        Returns:
            The result in the format set by output_type: the final report
            for "final", the full history for the others.
        """
        if task is None:
            raise ValueError(
                "task argument is required to run AdvancedResearch"
            )
        self._reset()
        self.conversation.add("human", task)

        report: Optional[str] = None
        gaps: List[str] = []
        for loop_num in range(self.max_loops):
            logger.info(
                f"Starting research loop {loop_num + 1}/{self.max_loops}"
            )
            round_result = self.step(task, img, report, gaps)
            report = round_result["report"]
            gaps = round_result["gaps"]
            logger.info(
                f"Completed research loop {loop_num + 1}/{self.max_loops}"
            )
            if not round_result["needs_more_research"] or not gaps:
                break

        cited = self._cite(report or "")
        references = build_references(cited, self.sources)
        final_report = (
            f"{cited}\n\n## References\n\n{references}"
            if references
            else cited
        )
        self.conversation.add("Citation-Agent", final_report)
        logger.info(
            f"Research finished: {len(self.sources.sources)} sources, ${self.total_cost:.4f} Swarms API cost"
        )

        if self.export_on:
            self._export_conversation()
        return self.conversation.format(self.output_type)

    def batched_run(self, tasks: List[str]) -> List[Any]:
        """Research each task in turn and return the results in order."""
        return [self.run(task) for task in tasks]

    def _export_conversation(self) -> None:
        """Save the session to examples/outputs/<id>.json."""
        output_file = f"examples/outputs/{self.id}.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        create_json_file(
            {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "conversation_history": self.conversation.get_history(),
                "sources": self.sources.sources,
                "total_cost_usd": round(self.total_cost, 6),
                "export_timestamp": datetime.now().isoformat(),
            },
            output_file,
        )
        logger.info(f"Conversation exported to {output_file}")

    def get_output_methods(self) -> List[str]:
        """Return the output_type values run() accepts."""
        return list(OUTPUT_TYPES)
