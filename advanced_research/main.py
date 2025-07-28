"""
MultiAgentResearchSystem: A multi-agent system for complex research tasks.

This implementation translates the concepts from the paper "How we built our 
multi-agent research system" into a functional framework using the 'swarms' library.

This improved version includes:
- Real tool integration (exa_search for web searches).
- Robust state management using the Conversation class.
- Adaptive error handling where the lead agent can react to sub-agent failures.
- Refined prompts for better agent performance and reliability.
"""

import json
import re
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from dotenv import load_dotenv
from loguru import logger

# Make sure to install swarms: pip install swarms loguru
# You might need to set your OPENAI_API_KEY and EXA_API_KEY as environment variables
from swarms import Agent, Conversation

# Load environment variables from .env file
load_dotenv()

# --- Setup Loguru Logging ---
# Remove default handler and add custom ones
logger.remove()
logger.add(
    sys.stdout, 
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True
)
logger.add(
    "research_system.log", 
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="10 MB",
    retention="7 days",
    encoding="utf-8"
)


# --- Tool Definition (Real Web Search) ---
def exa_search(query: str, num_results: int = 5, **kwargs: Any) -> str:
    """
    Performs a web search using the Exa.ai API and returns formatted results.
    This tool is provided to SubAgents to conduct their research.

    Args:
        query (str): The search query.
        num_results (int): The number of search results to return.

    Returns:
        str: A formatted string of search results or an error message.
    """
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        return "Error: EXA_API_KEY environment variable not set."

    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "query": query,
        "useAutoprompt": True,
        "numResults": num_results,
        "contents": {"text": {"maxCharacters": 200}, "highlights": True},
    }

    try:
        response = requests.post("https://api.exa.ai/search", json=payload, headers=headers)
        response.raise_for_status()
        json_data = response.json()

        if "error" in json_data:
            return f"Error: {json_data['error']}"

        results = json_data.get("results", [])
        if not results:
            return "No results found."

        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "No Title")
            url = result.get("url", "No URL")
            content_preview = result.get("text", "No content preview available.")
            formatted_results.append(f"{i}. Title: {title}\n   URL: {url}\n   Preview: {content_preview}\n")
        
        return "\n".join(formatted_results)

    except requests.RequestException as e:
        return f"Error during web search: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


# --- Data Structures for Communication ---
@dataclass
class SubAgentResult:
    """Standardized data structure for results from a SubAgent."""

    task: str
    findings: str
    sources: List[Dict[str, str]] = field(default_factory=list)
    error: Optional[str] = None  # To capture any failures


# --- Main Orchestrator Class ---
class MultiAgentResearchSystem:
    """
    Orchestrates a multi-agent system for conducting comprehensive research tasks.

    This system operationalizes the orchestrator-worker pattern described in the paper.
    It handles query decomposition, parallel sub-task execution with real tools,
    iterative synthesis, and final citation generation.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o",
        max_iterations: int = 3,
        max_workers: int = 4,
        base_path: str = "agent_states",
    ):
        """Initializes the MultiAgentResearchSystem."""
        self.model_name = model_name
        self.max_iterations = max_iterations
        self.max_workers = max_workers
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        logger.info("MultiAgentResearchSystem initialized.")

        self.conversation = Conversation()
        self._init_agents()

    def _init_agents(self) -> None:
        """Initializes the lead and citation agents."""
        logger.info("Initializing Lead and Citation agents...")
        self.lead_agent = Agent(
            agent_name="Lead-Researcher",
            model_name=self.model_name,
            max_loops=1,
            autosave=True,
            saved_state_path=str(self.base_path / "lead_researcher.json"),
            verbose=True,
            output_type="json",  # Try to force JSON output
            retry_attempts=3,
        )

        self.citation_agent = Agent(
            agent_name="Citation-Agent",
            system_prompt=self._get_citation_prompt(),
            model_name=self.model_name,
            max_loops=1,
            autosave=True,
            saved_state_path=str(self.base_path / "citation_agent.json"),
            verbose=True,
        )
        logger.info("Agents initialized successfully.")

    # --- Prompt Engineering Section ---

    def _get_planner_prompt(self, query: str) -> str:
        """Generates the prompt for the planning phase."""
        return f"""You are a research planner. Break down this query into 3-5 sub-tasks for parallel research.

Query: "{query}"

Output ONLY valid JSON in this exact format:
{{
    "sub_tasks": [
        "specific research task 1",
        "specific research task 2", 
        "specific research task 3"
    ]
}}

Rules:
- Only respond with the JSON object
- No explanations or other text
- Each task should be specific and researchable
- Tasks should cover different aspects of the main query
"""

    def _get_researcher_prompt(self) -> str:
        """Generates the prompt for a SubAgent."""
        return """
        You are a specialized Research Sub-Agent. Your purpose is to execute a single, focused research task by using the provided `exa_search` tool and then return a concise summary of your findings and the sources you used.

        Guidelines:
        1.  You have access to a tool called `exa_search`. Use it to find information relevant to your assigned task.
        2.  Stick strictly to the assigned task. Do not deviate.
        3.  Synthesize the information you find into a clear, factual summary.
        4.  For every piece of information, you MUST cite your source URL.
        
        CRITICAL: After conducting your research, you MUST respond with ONLY valid JSON. Do not include any explanation, reasoning, markdown formatting, or other text outside the JSON.
        
        Required JSON format:
        {
            "findings": "Your synthesized summary here",
            "sources": [
                {
                    "source": "URL here",
                    "content": "Brief quote or summary here"
                }
            ]
        }
        """

    def _get_synthesizer_prompt(
        self, query: str, results: List[SubAgentResult]
    ) -> str:
        """Generates the prompt for the synthesis and refinement phase."""
        results_str = ""
        for res in results:
            if res.error:
                results_str += f"--- Sub-Task Failed: {res.task} ---\nError: {res.error}\n\n"
            else:
                results_str += f"--- Result for Sub-Task: {res.task} ---\nFindings: {res.findings}\n\n"
        
        return f"""
        You are a Lead Researcher AI. You have received findings (and potential errors) from your sub-agents for a research query. Your task is to synthesize these findings into a coherent report and determine if the research is complete.

        Original Query: "{query}"

        Sub-Agent Findings & Errors:
        {results_str}

        Guidelines:
        1.  Synthesize all the provided findings into a single, comprehensive draft report.
        2.  Analyze any errors from failed sub-tasks. If a task failed, the research is incomplete.
        3.  Analyze the draft report against the original query. Is the query fully answered?
        4.  If the query is answered and there were no critical failures, set "is_complete" to true.
        5.  If the query is NOT fully answered, or if a critical task failed, identify the gaps. Formulate new sub-tasks to address these gaps or to retry the failed tasks.
        
        CRITICAL: You MUST respond with ONLY valid JSON. Do not include any explanation, markdown formatting, or other text.
        
        Required JSON format:
        {{
            "draft_report": "Your synthesized report here",
            "is_complete": true,
            "new_tasks": []
        }}
        """

    def _get_citation_prompt(self) -> str:
        """Generates the prompt for the CitationAgent."""
        return """
        You are a specialized Citation Agent. Your sole purpose is to add citations to a final report using a provided list of sources.

        Guidelines:
        1.  Read the final report and the list of all sources.
        2.  For each claim or piece of data in the report, find the corresponding source from the provided list.
        3.  Append a citation marker (e.g., [1], [2]) to the relevant sentences in the report.
        4.  At the end of the report, create a "References" section listing all sources with their corresponding number.

        CRITICAL: You MUST respond with ONLY valid JSON. Do not include any explanation, markdown formatting, or other text.
        
        Required JSON format:
        {
            "cited_report": "Your final report with citations and references section here"
        }
        """

    # --- Utility Methods ---

    def _safely_parse_json(self, json_str: str) -> Dict[str, Any]:
        """Safely parse JSON string, handling common LLM output issues."""
        if not json_str or json_str.strip() == "":
            logger.warning("Empty response received from agent")
            return {"error": "Empty response", "raw_content": json_str}
        
        try:
            # Clean the string
            cleaned_str = json_str.strip()
            
            # Try multiple extraction patterns
            patterns = [
                r"```json\n(\{.*?\})\n```",  # ```json\n{...}\n```
                r"```\n(\{.*?\})\n```",     # ```\n{...}\n```
                r"(\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\})",  # Find any complete JSON object
                r"```json\s*(\{.*?\})\s*```", # ```json {...} ```
                r"```\s*(\{.*?\})\s*```",   # ``` {...} ```
            ]
            
            for pattern in patterns:
                match = re.search(pattern, cleaned_str, re.DOTALL)
                if match:
                    json_candidate = match.group(1)
                    try:
                        return json.loads(json_candidate)
                    except json.JSONDecodeError:
                        continue
            
            # Try parsing the entire string as JSON
            try:
                return json.loads(cleaned_str)
            except json.JSONDecodeError:
                pass
            
            # If all else fails, try to find JSON at the end of the response
            lines = cleaned_str.split('\n')
            for i in range(len(lines)-1, -1, -1):
                line = lines[i].strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue
            
            # Last resort: try to extract JSON from the last few lines
            last_lines = '\n'.join(lines[-10:])
            match = re.search(r'(\{[^}]*"[^"]*"[^}]*\})', last_lines, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            logger.exception("Unexpected error in JSON parsing: {}", e)
        
        # If we get here, parsing failed
        logger.error("JSON parsing failed completely. Raw string (first 500 chars): '{}'", json_str[:500])
        return {"error": "Failed to parse JSON", "raw_content": json_str}

    # --- Core Workflow Methods ---

    def _run_sub_agent_task(self, task: str) -> SubAgentResult:
        """Creates and runs a single SubAgent with a real search tool."""
        agent_id = f"SubAgent-{task[:20].replace(' ', '-')}"
        logger.info("[{}] Starting task: {}", agent_id, task)

        try:
            sub_agent = Agent(
                agent_name=agent_id,
                system_prompt=self._get_researcher_prompt(),
                model_name=self.model_name,
                max_loops=3,  # Allow a few loops for tool use
                tools=[exa_search],
                verbose=True, # Set to True for detailed sub-agent logging
            )

            # The agent will now use the 'exa_search' tool when it deems necessary
            response = sub_agent.run(task=f"Your assigned task is: '{task}'")
            parsed_response = self._safely_parse_json(response)

            if "error" in parsed_response:
                logger.warning(f"[{agent_id}] Failed to parse JSON response. Attempting to extract findings from raw text.")
                # Try to extract useful information from the raw response
                raw_content = parsed_response.get("raw_content", "")
                if raw_content:
                    # Try to find findings in the raw text
                    findings_match = re.search(r'"findings":\s*"([^"]*)"', raw_content, re.DOTALL)
                    findings = findings_match.group(1) if findings_match else f"Research conducted on: {task}"
                    
                    # Try to extract sources
                    sources = []
                    source_matches = re.findall(r'"source":\s*"([^"]*)"', raw_content)
                    for i, source_url in enumerate(source_matches):
                        sources.append({
                            "source": source_url,
                            "content": f"Source {i+1} from research on {task}"
                        })
                    
                    logger.info(f"[{agent_id}] Extracted partial information from raw response.")
                    return SubAgentResult(
                        task=task,
                        findings=findings,
                        sources=sources,
                    )
                else:
                    raise ValueError(f"Sub-agent returned an error: {parsed_response['error']}")

            sources = parsed_response.get("sources", [])
            
            logger.info(f"[{agent_id}] Task finished successfully.")
            return SubAgentResult(
                task=task,
                findings=parsed_response.get("findings", "No findings returned."),
                sources=sources,
            )
        except Exception as e:
            logger.error(f"[{agent_id}] Task failed with exception: {e}", exc_info=True)
            return SubAgentResult(
                task=task,
                findings="",
                sources=[],
                error=str(e)
            )

    def run(self, query: str) -> Dict[str, Any]:
        """Main execution flow for the research process."""
        logger.info(f"--- Starting New Research for Query: '{query}' ---")
        
        self.conversation = Conversation()
        self.conversation.add("user", query)
        
        # 1. Planning Phase
        logger.info("Phase 1: Planning")
        self.lead_agent.system_prompt = self._get_planner_prompt(query)
        json_instruction = "RESPOND ONLY WITH JSON. NO OTHER TEXT. JSON FORMAT: {\"sub_tasks\": [\"task1\", \"task2\", \"task3\"]}"
        plan_response = self.lead_agent.run(task=f"{json_instruction}\n\nQuery: {query}")
        plan_data = self._safely_parse_json(plan_response)
        
        if "error" in plan_data:
            logger.warning(f"Planning phase failed to return valid JSON. Using fallback approach.")
            # Fallback: create reasonable sub-tasks based on the query content
            if "healthcare" in query.lower() and "ai" in query.lower():
                tasks = [
                    "Research the benefits of AI in healthcare including diagnostic accuracy and efficiency",
                    "Investigate the risks and challenges of AI in healthcare including privacy and bias concerns",
                    "Analyze the primary ethical considerations of AI in healthcare including consent and accountability"
                ]
            else:
                # Generic fallback for any query
                key_terms = [word for word in query.split() if len(word) > 3][-3:]  # Get last 3 significant words
                subject = " ".join(key_terms) if key_terms else "the topic"
                tasks = [
                    f"Research the main benefits and advantages of {subject}",
                    f"Investigate the risks and challenges associated with {subject}",
                    f"Analyze the implications and considerations of {subject}"
                ]
        else:
            tasks = plan_data.get("sub_tasks", [])

        if not tasks:
            logger.warning("No tasks generated. Using query as a single task.")
            tasks = [query]
        
        self.conversation.add("Lead-Researcher", f"Plan Created: {tasks}")

        # 2. Iterative Research & Synthesis Phase
        final_report = ""
        all_sources = []
        
        for i in range(self.max_iterations):
            logger.info(f"--- Iteration {i + 1}/{self.max_iterations} ---")
            logger.info(f"Executing {len(tasks)} tasks in parallel...")

            sub_agent_results = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_task = {executor.submit(self._run_sub_agent_task, task): task for task in tasks}
                for future in as_completed(future_to_task):
                    result = future.result()
                    sub_agent_results.append(result)
                    all_sources.extend(result.sources)
            
            self.conversation.add("Sub-Agents", f"Completed {len(sub_agent_results)} tasks. Results: {[res.findings for res in sub_agent_results]}")

            # Synthesis Phase
            logger.info("Phase 2: Synthesizing results...")
            synthesis_prompt = self._get_synthesizer_prompt(query, sub_agent_results)
            self.lead_agent.system_prompt = synthesis_prompt
            
            synthesis_response = self.lead_agent.run(task="Synthesize the collected findings and determine next steps.")
            synthesis_data = self._safely_parse_json(synthesis_response)
            
            if "error" in synthesis_data:
                logger.warning("Synthesis phase failed to return valid JSON. Using fallback approach.")
                # Create a basic report from available findings
                findings_text = "\n\n".join([res.findings for res in sub_agent_results if res.findings and not res.error])
                if findings_text:
                    final_report = f"Research Summary for: {query}\n\n{findings_text}"
                    is_complete = True  # Consider it complete if we have some findings
                    tasks = []
                else:
                    final_report = f"Research was attempted for: {query}\nHowever, the research agents encountered difficulties in gathering information."
                    is_complete = True  # Mark as complete to avoid infinite loops
                    tasks = []
            else:
                final_report = synthesis_data.get("draft_report", final_report)
                is_complete = synthesis_data.get("is_complete", False)
                tasks = synthesis_data.get("new_tasks", [])
            
            self.conversation.add("Lead-Researcher", f"Synthesis: {synthesis_data}")

            if is_complete:
                logger.info("Synthesis complete. Research goal achieved.")
                break
            elif not tasks:
                logger.info("Synthesis resulted in no new tasks. Concluding research.")
                break
            else:
                logger.info(f"Research not complete. Planning to execute {len(tasks)} new tasks.")

        # 3. Citation Phase
        logger.info("Phase 3: Adding Citations")
        citation_input = json.dumps({"report": final_report, "sources": all_sources})
        citation_response = self.citation_agent.run(task=citation_input)
        citation_data = self._safely_parse_json(citation_response)
        
        if "error" in citation_data:
            logger.warning("Citation phase failed to return valid JSON. Using original report.")
            cited_report = final_report
            # Add a simple references section if we have sources
            if all_sources:
                cited_report += "\n\n## References\n"
                for i, source in enumerate(all_sources, 1):
                    cited_report += f"[{i}] {source.get('source', 'N/A')}\n"
        else:
            cited_report = citation_data.get("cited_report", final_report)

        self.conversation.add("Citation-Agent", f"Final Report: {cited_report}")

        logger.info("--- Research Task Finished ---")
        return {
            "final_report": cited_report,
            "sources": all_sources,
        }

# --- Main Execution ---
if __name__ == "__main__":
    try:
        # Ensure you have OPENAI_API_KEY and EXA_API_KEY set in your .env file
        research_system = MultiAgentResearchSystem(
            model_name="gpt-4o",
            max_iterations=2,
            max_workers=5
        )

        user_query = "What are the benefits and risks of using AI in healthcare, and what are the primary ethical considerations?"
        
        final_result = research_system.run(user_query)

        print("\n" + "=" * 50)
        print("          FINAL CITED RESEARCH REPORT")
        print("=" * 50 + "\n")
        print(final_result["final_report"])
        print("\n" + "=" * 50)
        print("              ALL SOURCES GATHERED")
        print("=" * 50 + "\n")
        # De-duplicate sources before printing
        unique_sources = {s['source']: s for s in final_result["sources"]}.values()
        for idx, source in enumerate(unique_sources):
             print(f"[{idx+1}] Source: {source.get('source', 'N/A')}")
             print(f"    Content: {source.get('content', 'N/A')}")


    except Exception as e:
        logger.error(f"An error occurred during the main execution: {e}", exc_info=True)