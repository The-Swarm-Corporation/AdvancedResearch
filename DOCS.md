# Advanced Research System - API Documentation

## Table of Contents

- [Overview](#overview)
- [AdvancedResearch Class](#advancedresearch-class)
  - [Constructor Parameters](#constructor-parameters)
  - [Methods](#methods)
  - [Attributes](#attributes)
- [Functions](#functions)
- [Types and Enums](#types-and-enums)
- [Configuration Examples](#configuration-examples)
- [Error Handling](#error-handling)
- [Environment Variables](#environment-variables)
- [File Outputs](#file-outputs)

## Overview

AdvancedResearch implements the orchestrator-worker pattern from Anthropic's ["How we built our multi-agent research system"](https://www.anthropic.com/research/multi-agent-research-system) on two APIs:

- **Swarms API** (`https://api.swarms.world/v1/agent/completions`) runs every agent: the lead researcher, the search subagents and the citation agent.
- **Exa** (`https://api.exa.ai/search`) is the web search the subagents use.

A run goes through four stages:

1. **Plan.** The lead researcher judges the query's complexity (simple, comparison, complex) and writes one subtask per subagent: an objective, 2 or 3 search queries, an output format and boundaries.
2. **Search.** The subagents run in parallel. Each round, a subagent searches Exa for its queries in parallel, the results are added to a numbered source list shared by the whole run, and the subagent records findings that cite those numbers. It can ask for narrower follow-up searches, which run in the next round, up to `worker_search_rounds`.
3. **Report.** The lead researcher writes the report from all findings and ends it with a decision: does a gap need another research round? If so, and `max_loops` allows, the next round plans subtasks for the gaps only.
4. **Cite.** The citation agent checks each claim against the source text of the sources cited, and fixes or removes unsupported citations. A references section is built from the sources the final report cites.

## AdvancedResearch Class

```python
from advanced_research import AdvancedResearch
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `str \| None` | new id per instance | Session id, used for the export file name |
| `name` | `str` | `"Advanced Research"` | Name of the research system |
| `description` | `str` | `"Advanced Research"` | Description of the research system |
| `worker_model_name` | `str` | `"gpt-5.4-mini"` | Swarms API model for the search subagents |
| `worker_max_tokens` | `int` | `3000` | Maximum output tokens per subagent call |
| `director_agent_name` | `str` | `"Director-Agent"` | Name of the lead researcher |
| `director_model_name` | `str` | `"gpt-5.5"` | Swarms API model for planning, the report and the citation pass |
| `director_max_tokens` | `int` | `4000` | Maximum output tokens for the report and citation calls (planning uses at most 2000) |
| `output_type` | `str` | `"final"` | What `run()` returns; see [Output types](#output-types) |
| `max_loops` | `int` | `1` | Most research rounds. The lead stops early when the report has no gaps worth another round |
| `export_on` | `bool` | `False` | Save the session to `examples/outputs/<id>.json` after each run |
| `director_max_loops` | `int` | `1` | Agent loops for each lead researcher call |
| `verbose` | `bool` | `False` | Print every agent reply (plan, search subagents, report, citations) to the console as it arrives |
| `config` | `AdvancedResearchAdditionalConfig \| None` | module defaults | Subagent and search settings; see [AdvancedResearchAdditionalConfig](#advancedresearchadditionalconfig) |

`output_type` must be one of the output types, or the constructor raises `ValueError`.

### Methods

#### `run(task: str, img: Optional[str] = None) -> Any`

Research the task and return the result in the format set by `output_type`. With `"final"` that is the cited report in Markdown, ending with a `## References` section.

`img` is an optional `https://` image URL or base64 image; the lead researcher sees it when planning.

```python
research = AdvancedResearch(max_loops=2)
report = research.run("How do solid-state batteries compare with lithium-ion in 2026?")
print(report)
print(f"Swarms API cost: ${research.total_cost:.4f}")
```

Each call to `run()` starts a fresh session: the conversation, sources and cost are reset.

#### `step(task, img=None, previous_report=None, gaps=None) -> dict`

Run one research round (plan, search, report) without the citation pass. Returns:

```python
{
    "plan": {"complexity": "...", "strategy": "...", "subtasks": [...]},
    "report": "Markdown report with [n] citations",
    "needs_more_research": False,
    "gaps": [],
}
```

`run()` calls `step()` once per round. Use it directly to inspect or steer the rounds yourself.

#### `batched_run(tasks: List[str]) -> List[Any]`

Run each task in turn and return the results in order.

#### `get_output_methods() -> List[str]`

Return the accepted `output_type` values.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `conversation` | `Conversation` | The session history: the query, each plan, each subagent's findings, the final report |
| `sources` | `SourceRegistry` | Every source found, numbered; `sources.sources` is the list in citation order |
| `worker_results` | `List[dict]` | Each subagent's objective, findings, key facts, conflicts, searches, source numbers, confidence and cost |
| `total_cost` | `float` | The session's Swarms API cost in USD, summed from each response's `usage.total_cost`. Exa is billed separately by Exa |
| `config` | `AdvancedResearchAdditionalConfig` | The settings the subagents use |

## Functions

All are in `advanced_research.main`.

### `swarms_agent(agent_name, system_prompt, task, model_name, max_tokens, img=None, max_loops=1) -> (str, float)`

Run one agent on the Swarms API and return its reply text and the call's cost in USD.

### `exa_search(query, num_results, max_characters) -> List[dict]`

Search Exa and return results as dicts with `url`, `title`, `published_date`, `text` and `highlights`.

### `run_agent(i, query, registry=None, config=schema) -> dict`

Run one search subagent. `query` is a question or a subtask dict with `objective`, `search_queries`, `output_format` and `boundaries`.

### `run_worker_agents(subtasks, registry=None, config=schema) -> List[dict]`

Run one subagent per subtask in parallel. A subagent that fails returns its error in its result instead of failing the round.

### `execute_worker_search_agents(queries: List[str]) -> str`

Research each query with its own subagent and return the findings as one string.

### `create_director_agent(agent_name, model_name, task, img=None, max_loops=1, max_tokens=..., max_subagents=5) -> (dict, float)`

Run the lead researcher's planning step and return the plan and its cost. If the reply has no usable plan, the query is researched as a single subtask.

### `build_references(report, registry) -> str`

Return a references list for the sources the report cites, in citation-number order. Citation numbers that are not in the registry are left out.

### `generate_id() -> str`

Return a session id like `AdvancedResearch-<uuid>-time-<YYYYMMDDHHMMSS>`.

### `create_json_file(data: dict, file_name: str) -> None`

Write `data` to a JSON file, merging into the file's existing object if it has one.

## Types and Enums

### Output types

| `output_type` | `run()` returns |
|---------------|-----------------|
| `"final"`, `"last"` | The cited report (Markdown string) |
| `"list"`, `"dict"` | The full history as a list of `{"role", "content", "timestamp"}` dicts |
| `"json"` | The full history as a JSON string |
| `"markdown"` | The full history as Markdown, one `###` section per message |
| `"all"`, `"str"`, `"string"` | The full history as `role: content` text |

### AdvancedResearchAdditionalConfig

```python
from advanced_research import AdvancedResearchAdditionalConfig

config = AdvancedResearchAdditionalConfig(
    worker_model_name="gpt-5.4-mini",
    worker_max_tokens=3000,
    exa_search_num_results=5,
    exa_search_max_characters=1500,
    worker_search_rounds=2,
    max_subagents=5,
)
```

| Field | Default | Description |
|-------|---------|-------------|
| `worker_model_name` | `"gpt-5.4-mini"` | Swarms API model for the subagents |
| `worker_max_tokens` | `3000` | Maximum output tokens per subagent call |
| `exa_search_num_results` | `5` | Results per Exa search |
| `exa_search_max_characters` | `1500` | Page-text characters kept per result |
| `worker_search_rounds` | `2` | Search rounds per subagent: the planned queries, then follow-ups |
| `max_subagents` | `5` | Most subagents per research round |

The constructor's `worker_model_name` and `worker_max_tokens` override the config's values.

## Configuration Examples

### Basic Research Setup

```python
from advanced_research import AdvancedResearch

research = AdvancedResearch()
print(research.run("What are the latest developments in quantum error correction?"))
```

### Advanced Multi-Loop Research

```python
from advanced_research import AdvancedResearch, AdvancedResearchAdditionalConfig

research = AdvancedResearch(
    director_model_name="claude-sonnet-5",
    max_loops=3,
    config=AdvancedResearchAdditionalConfig(
        worker_search_rounds=3,
        max_subagents=8,
        exa_search_num_results=8,
    ),
)
report = research.run("Compare national AI safety institutes: mandates, budgets and output so far")
```

More subagents, rounds and results mean more Swarms API calls and Exa searches, so a run costs more and takes longer.

### Batch Processing Setup

```python
research = AdvancedResearch(export_on=True)
reports = research.batched_run([
    "Latest advances in grid-scale energy storage",
    "Current state of autonomous trucking regulation",
])
```

### Custom Output Format

```python
research = AdvancedResearch(output_type="markdown")
history = research.run("What changed in EU AI Act obligations this year?")
```

## Error Handling

API failures raise `advanced_research.main.ResearchAPIError` with the service, status and response text.

- **Missing keys.** `SWARMS_API_KEY` or `EXA_API_KEY` not set raises `ResearchAPIError` naming the variable.
- **Retries.** Connection errors, 429s and short-lived 500, 502 and 503 responses are retried up to 3 times with backoff.
- **The 30-second limit.** A Swarms API request ends after 30 seconds. A 503 or 504 after that long is not retried, because it would run the same slow call again; the error suggests a faster model or a lower `max_tokens`.
- **A failing subagent** doesn't stop the run: its result carries the error and the report notes the gap.
- **A failing citation pass** keeps the report's existing citations.
- **Unparseable replies.** A plan with no usable subtasks falls back to one subtask for the whole query, and a subagent reply that isn't JSON is used as plain findings.

## Environment Variables

```bash
SWARMS_API_KEY="..."   # https://swarms.world/platform/api-keys
EXA_API_KEY="..."      # https://dashboard.exa.ai/api-keys

# Optional
SWARMS_BASE_URL="https://api.swarms.world"
EXA_BASE_URL="https://api.exa.ai"
```

Models and token limits are constructor arguments on `AdvancedResearch` (and Exa search size is on `AdvancedResearchAdditionalConfig`), not environment variables. Any model from `GET https://api.swarms.world/v1/models/available` works for either role.

## File Outputs

With `export_on=True`, each run writes `examples/outputs/<id>.json`:

```json
{
  "id": "AdvancedResearch-...-time-20261108120000",
  "name": "Advanced Research",
  "description": "Advanced Research",
  "conversation_history": [{"role": "human", "content": "...", "timestamp": "..."}],
  "sources": [{"url": "...", "title": "...", "published_date": "...", "text": "...", "highlights": ["..."]}],
  "total_cost_usd": 0.0427,
  "export_timestamp": "2026-11-08T12:00:30"
}
```
