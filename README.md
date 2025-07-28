![Anthropic Multi-Agent Architecture](https://storage.googleapis.com/gweb-research2023-media/images/Group_88.width-1250.png)

# Multi-Agent Research System (Based on Anthropic's Paper)

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/swarms-999382051935506503) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)

An implementation of the orchestrator-worker pattern from Anthropic's paper, ["How we built our multi-agent research system,"](https://www.anthropic.com/news/how-we-built-our-multi-agent-research-system) using the `swarms` framework. This system decomposes complex research queries into parallelizable sub-tasks, executes them with specialized agents, and iteratively synthesizes the findings into a comprehensive, cited report.

## Features

🧠 **Orchestrator-Worker Architecture**: A `LeadResearcherAgent` plans, delegates, and synthesizes, while dynamically created `SubAgents` execute focused tasks.
🌐 **Real Tool Integration**: Utilizes `exa_search` for real-time, relevant web searches, grounding the research in factual data.
🔄 **Iterative Refinement**: The lead agent analyzes results from sub-agents and generates new tasks if the research is incomplete, creating a powerful feedback loop.
⚡ **Parallel Research Execution**: Leverages a `ThreadPoolExecutor` to run multiple `SubAgents` concurrently, drastically speeding up the information-gathering process.
✍️ **Automated Citation Generation**: A specialized `CitationAgent` processes the final report and sources to add academic-style citations, ensuring credibility.
🛡️ **Adaptive Error Handling**: The lead agent is designed to receive and understand errors from sub-agents, allowing it to adapt its plan and retry failed tasks.
💾 **State Persistence**: Built on the `swarms` Agent class, allowing for agent states to be saved and resumed.

## Architecture

The system follows a dynamic, multi-phase workflow orchestrated by the `LeadResearcherAgent`.

```
                [User Query]
                     │
                     ▼
        ┌─────────────────────────┐
        │ LeadResearcherAgent     │ (Orchestrator)
        └─────────────────────────┘
                     │ 1. Plan & Decompose
                     ▼
    ┌───────────────────────────────────┐
    │       Parallel Sub-Tasks          │
    └───────────────────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌───────────┐   ┌───────────┐   ┌───────────┐
│ SubAgent 1│   │ SubAgent 2│   │ SubAgent 3│ (Workers)
│ (Search)  │   │ (Search)  │   │ (Search)  │
└───────────┘   └───────────┘   └───────────┘
       │              │              │
       ▼              ▼              ▼
    ┌───────────────────────────────────┐
    │     Aggregated Sub-Agent Results    │
    └───────────────────────────────────┘
                     │ 2. Synthesize & Refine
                     ▼
        ┌─────────────────────────┐
        │ LeadResearcherAgent     │
        └─────────────────────────┘
                     │ 3. Generate Final Report
                     ▼
        ┌─────────────────────────┐
        │      CitationAgent      │ (Post-Processor)
        └─────────────────────────┘
                     │ 4. Add Citations
                     ▼
              [Final Cited Report]
```

### Workflow Process

1.  **Planning Phase**: The `LeadResearcherAgent` analyzes the user's query and decomposes it into a list of specific, parallelizable sub-tasks.
2.  **Parallel Research Phase**: Multiple `SubAgents` are dynamically created, each assigned one sub-task. They execute their research concurrently using the `exa_search` tool.
3.  **Iterative Synthesis Phase**: The `LeadResearcherAgent` gathers all findings and errors from the `SubAgents`. It synthesizes a draft report and determines if the original query is fully answered. If not, it generates new sub-tasks to fill the gaps and the research phase repeats.
4.  **Citation Phase**: Once the research is complete, the final draft report and all collected sources are passed to a `CitationAgent`, which adds inline citations and a "References" section.

## Installation

### Prerequisites

-   Python 3.10 or higher
-   API keys for an LLM provider (e.g., OpenAI) and Exa

### Install from PyPI

The `MultiAgentResearchSystem` is built using the `swarms` framework.

```bash
pip install -U swarms
pip install python-dotenv requests beautifulsoup4
```

### Environment Setup

Create a `.env` file in your project root with your API keys:

```bash
OPENAI_API_KEY="your_openai_api_key_here"
EXA_API_KEY="your_exa_api_key_here"
```

## Quick Start

Save the implementation code as `multi_agent_research_system.py` and run the following:

```python
from multi_agent_research_system import MultiAgentResearchSystem

# Initialize the research system
# You can customize the model, max iterations, and parallel workers
research_system = MultiAgentResearchSystem(
    model_name="gpt-4o",
    max_iterations=2,
    max_workers=5
)

# Define your research goal
research_goal = (
    "What are the primary benefits and risks of using generative AI"
    " in financial analysis, and what are the key ethical considerations?"
)

# Run the research workflow
results = research_system.run(research_goal)

# Print the final, cited report
print("\n" + "="*50)
print("          FINAL CITED RESEARCH REPORT")
print("="*50 + "\n")
print(results["final_report"])

# Print all unique sources gathered during the research
print("\n" + "="*50)
print("              ALL SOURCES GATHERED")
print("="*50 + "\n")
unique_sources = {s['source']: s for s in results["sources"]}.values()
for idx, source in enumerate(unique_sources, 1):
    print(f"[{idx}] Source: {source.get('source', 'N/A')}")
    print(f"    Content Preview: {source.get('content', 'N/A')}")

```

## Advanced Usage

### Custom Configuration

You can easily customize the behavior of the research system during initialization.

```python
# Use a different model, allow more iterations, and increase parallelism
custom_research_system = MultiAgentResearchSystem(
    model_name="claude-3-opus-20240229",
    max_iterations=4,
    max_workers=8,
    base_path="./custom_research_states"
)

results = custom_research_system.run(
    "Explore the long-term societal impact of autonomous transportation."
)
```

### Accessing Intermediate Results

The `run` method returns a dictionary containing not just the final report but also all the sources and raw findings from the sub-agents, which can be useful for analysis and debugging.

```python
results = research_system.run(research_goal)

# All unique sources found
unique_sources = {s['source']: s for s in results["sources"]}.values()

# All intermediate results from sub-agents
sub_agent_results = results['sub_agent_results']
for res in sub_agent_results:
    print(f"Task: {res['task']}")
    print(f"Findings: {res['findings']}")
    if res['error']:
        print(f"Error: {res['error']}")
```

## 🤝 Contributing

This implementation is part of the open-source `swarms` framework. We welcome contributions! Please feel free to open an issue or submit a pull request on the [main repository](https://github.com/kyegomez/swarms).

1.  Fork the `swarms` repository.
2.  Create a feature branch (`git checkout -b feature/amazing-research-feature`).
3.  Commit your changes (`git commit -m 'Add amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-research-feature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/kyegomez/swarms/blob/master/LICENSE) file for details.

## 📚 Citation

If you use this work in your research, please cite both the original paper and the `swarms` software implementation.

```bibtex
@misc{anthropic2024researchsystem,
    title={How we built our multi-agent research system},
    author={Anthropic},
    year={2024},
    month={June},
    url={https://www.anthropic.com/news/how-we-built-our-multi-agent-research-system}
}

@software{swarms_framework,
    title={Swarms: An Open-Source Multi-Agent Framework},
    author={Kye Gomez},
    year={2023},
    url={https://github.com/kyegomez/swarms}
}
```

## 🔗 Related Work

-   [Original Paper](https://www.anthropic.com/news/how-we-built-our-multi-agent-research-system) - "How we built our multi-agent research system" by Anthropic
-   [Swarms Framework](https://github.com/kyegomez/swarms) - The underlying multi-agent AI orchestration framework

## 📞 Support

-   **Issues**: [Swarms GitHub Issues](https://github.com/kyegomez/swarms/issues)
-   **Email**: kye@swarms.world
-   **Discord**: [Join our community](https://discord.gg/swarms-999382051935506503)

## 📝 TODO

-   [ ] **Add More Tools**: Integrate more search tools like Google Search, ArXiv, and PubMed for broader research capabilities.
-   [ ] **Implement Advanced Memory**: Replace the in-memory state with a persistent vector database for long-term memory across runs.
-   [ ] **Enhance Error Recovery**: Improve the `LeadResearcherAgent`'s ability to create more sophisticated recovery plans when sub-tasks fail.
-   [ ] **Add Visualization**: Create visualizations for the task decomposition and agent interaction flow.
-   [ ] **Optimize Prompts**: Further refine agent prompts for higher reliability and better performance on complex queries.

---

<p align="center">
  <strong>Built with <a href="https://github.com/kyegomez/swarms">Swarms</a> for advanced, autonomous AI research</strong>
</p>