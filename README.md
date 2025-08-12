![Anthropic Multi-Agent Architecture](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F1198befc0b33726c45692ac40f764022f4de1bf2-4584x2579.png&w=3840&q=75)

# Advanced Research System (Based on Anthropic's Paper)

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/EamjgSaEQf) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)

[![PyPI version](https://badge.fury.io/py/advancedresearch.svg)](https://badge.fury.io/py/advanced_research)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enhanced implementation of the orchestrator-worker pattern from Anthropic's paper, ["How we built our multi-agent research system"](https://www.anthropic.com/engineering/built-multi-agent-research-system), built on top of the bleeding-edge multi-agent framework `swarms`. Our implementation of this advanced research system leverages parallel execution, LLM-as-judge evaluation, and professional report generation with export capabilities.



## 📦 Installation

```bash
pip3 install -U advanced-research

# Or 
# uv pip install -U advanced-research

```

### Environment Setup

Create a `.env` file in your project root:

```bash
# Claude API Key (Primary LLM)
ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Exa Search API Key
EXA_API_KEY="your_exa_api_key_here"

# Optional: OpenAI API Key (alternative LLM)
OPENAI_API_KEY="your_openai_api_key_here"
```

## 🚀 Quick Start

### Basic Usage

```python
from advanced_research import AdvancedResearch

# Initialize the research system
research_system = AdvancedResearch(
    name="AI Research Team",
    description="Specialized AI research system",
    max_loops=1,
)

# Run research and get results
result = research_system.run(
    "What are the latest developments in quantum computing?"
)
print(result)
```

### With Export Functionality

```python
from advanced_research import AdvancedResearch

# Initialize with export enabled
research_system = AdvancedResearch(
    name="Quantum Computing Research",
    description="Research team focused on quantum computing advances",
    max_loops=1,
    export_on=True,  # Enable JSON export
)

# Run research - will automatically export to JSON file
research_system.run(
    "What are the latest developments in quantum computing?"
)
# Results will be saved to a timestamped JSON file
```

### Advanced Configuration

```python
from advanced_research import AdvancedResearch

# Initialize with custom settings
research_system = AdvancedResearch(
    name="Medical Research Team",
    description="Specialized medical research system",
    director_model_name="claude-3-5-sonnet-20250115",  # Use latest Claude model
    worker_model_name="claude-3-5-sonnet-20250115",
    director_max_tokens=10000,
    max_loops=2,  # Multiple research iterations
    output_type="all",  # Include full conversation history
    export_on=True,
)

# Run research with image input (if applicable)
result = research_system.run(
    "What are the most effective treatments for Type 2 diabetes?",
    img=None  # Optional image input
)
```

### Batch Processing Multiple Queries

```python
from advanced_research import AdvancedResearch

# Initialize the system
research_system = AdvancedResearch(
    name="Batch Research System",
    max_loops=1,
    export_on=True,
)

# Process multiple research tasks
tasks = [
    "Latest advances in renewable energy storage",
    "Current state of autonomous vehicle technology",
    "Recent breakthroughs in cancer immunotherapy"
]

# Run batch processing
research_system.batched_run(tasks)
```

### Using Different Output Formats

```python
from advanced_research import AdvancedResearch

# Initialize with specific output type
research_system = AdvancedResearch(
    name="Research System",
    output_type="json",  # Options: "all", "json", "markdown"
    export_on=False,  # Get results directly instead of exporting
)

# Run research and get formatted output
result = research_system.run(
    "What are the key challenges in AGI development?"
)

# Check available output methods
available_formats = research_system.get_output_methods()
print(f"Available output formats: {available_formats}")
```

## 📋 Quick Reference

| Task | Code | Documentation |
|------|------|---------------|
| **Basic Research** | `AdvancedResearch().run("query")` | [Basic Usage →](DOCS.md#basic-research-setup) |
| **Export Results** | `AdvancedResearch(export_on=True)` | [Export Config →](DOCS.md#configuration-examples) |
| **Batch Processing** | `system.batched_run([queries])` | [Batch Processing →](DOCS.md#batch-processing-setup) |
| **Custom Models** | `AdvancedResearch(director_model_name="model")` | [Advanced Config →](DOCS.md#advanced-multi-loop-research) |
| **Output Formats** | `AdvancedResearch(output_type="json")` | [Output Types →](DOCS.md#types-and-enums) |

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Orchestrator-Worker Architecture** | A `Director Agent` coordinates research strategy while specialized worker agents execute focused search tasks with Exa API integration. |
| **Advanced Web Search Integration** | Utilizes `exa_search` with structured JSON responses, content summarization, and intelligent result extraction for comprehensive research. |
| **High-Performance Parallel Execution** | Leverages `ThreadPoolExecutor` to run multiple specialized agents concurrently, achieving significant time reduction for complex queries. |
| **Flexible Configuration** | Customizable model selection (Claude, GPT), token limits, loop counts, and output formatting options. |
| **Conversation Management** | Built-in conversation history tracking with the `swarms` framework's `Conversation` class for persistent dialogue management. |
| **Export Functionality** | JSON export with automatic timestamping, unique session IDs, and comprehensive conversation history. |
| **Multiple Output Formats** | Support for various output types including JSON, markdown, and full conversation history formatting. |
| **Session Management** | Unique session IDs, batch processing capabilities, and step-by-step research execution control. |

## 🏗️ Architecture

The system follows a streamlined orchestrator-worker pattern with parallel execution:

```
                [User Query + Configuration]
                            │
                            ▼
           ┌─────────────────────────────────┐
           │       AdvancedResearch          │ (Main Orchestrator)
           │  - Session Management          │
           │  - Conversation History        │
           │  - Export Control              │
           └─────────────────────────────────┘
                            │ 1. Initialize Research Session
                            ▼
           ┌─────────────────────────────────┐
           │      Director Agent             │ (Research Coordinator)
           │  - Query Analysis & Planning    │
           │  - Task Decomposition           │
           │  - Research Strategy            │
           └─────────────────────────────────┘
                            │ 2. Decompose into Sub-Tasks
                            ▼
       ┌─────────────────────────────────────────┐
       │     Parallel Worker Execution           │
       │   (ThreadPoolExecutor - Concurrent)     │
       └─────────────────────────────────────────┘
          │           │           │           │
          ▼           ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │Worker 1  │ │Worker 2  │ │Worker 3  │ │Worker N  │
    │Exa Search│ │Exa Search│ │Exa Search│ │Exa Search│
    │Integration│ │Integration│ │Integration│ │Integration│
    └──────────┘ └──────────┘ └──────────┘ └──────────┘
          │           │           │           │
          ▼           ▼           ▼           ▼
       ┌─────────────────────────────────────────┐
       │      Results Aggregation                │
       │  - Combine Worker Outputs               │
       │  - Format Research Findings             │
       └─────────────────────────────────────────┘
                            │ 3. Synthesize Results
                            ▼
           ┌─────────────────────────────────┐
           │    Conversation Management      │
           │  - History Tracking             │
           │  - Output Formatting            │
           │  - Export Processing            │
           └─────────────────────────────────┘
                            │ 4. Deliver Results
                            ▼
              [Formatted Report + Optional JSON Export]
```

### 🔄 Workflow Process

1. **Session Initialization**: `AdvancedResearch` creates a unique research session with conversation tracking
2. **Director Agent Planning**: The director agent analyzes the query and plans research strategy
3. **Parallel Worker Execution**: Multiple worker agents execute concurrent searches using Exa API
4. **Results Aggregation**: Worker outputs are combined and synthesized into comprehensive findings
5. **Output Processing**: Results are formatted according to specified output type (JSON, markdown, etc.)
6. **Export & Delivery**: Optional JSON export with timestamped files and conversation history


## 🤝 Contributing

This implementation is part of the open-source `swarms` ecosystem. We welcome contributions!

1. Fork the [repository](https://github.com/The-Swarm-Corporation/AdvancedResearch)
2. Create a feature branch (`git checkout -b feature/amazing-research-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-research-feature`)
5. Open a Pull Request

### Development Setup with uv

```bash
# Clone and setup development environment
git clone https://github.com/The-Swarm-Corporation/AdvancedResearch.git
cd AdvancedResearch

uv venv

uv pip install -r requirements.txt
```

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/The-Swarm-Corporation/AdvancedResearch/blob/main/LICENSE) file for details.

## 📚 Citation

If you use this work in your research, please cite both the original paper and this implementation:

```bibtex
@misc{anthropic2024researchsystem,
    title={How we built our multi-agent research system},
    author={Anthropic},
    year={2024},
    month={June},
    url={https://www.anthropic.com/engineering/built-multi-agent-research-system}
}

@software{advancedresearch2024,
    title={AdvancedResearch: Enhanced Multi-Agent Research System},
    author={The Swarm Corporation},
    year={2024},
    url={https://github.com/The-Swarm-Corporation/AdvancedResearch},
    note={Implementation based on Anthropic's multi-agent research system paper}
}

@software{swarms_framework,
    title={Swarms: An Open-Source Multi-Agent Framework},
    author={Kye Gomez},
    year={2023},
    url={https://github.com/kyegomez/swarms}
}
```

## 📚 Documentation

For comprehensive API documentation, examples, and advanced usage:

**[📖 View Full API Documentation →](DOCS.md)**

The documentation includes:
- Complete API reference for the `AdvancedResearch` class
- Method signatures and parameter details
- Configuration examples and best practices
- Error handling and troubleshooting
- Output format specifications

## 🔗 Related Work

- [Original Paper](https://www.anthropic.com/engineering/built-multi-agent-research-system) - "How we built our multi-agent research system" by Anthropic
- [Swarms Framework](https://github.com/kyegomez/swarms) - The underlying multi-agent AI orchestration framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/The-Swarm-Corporation/AdvancedResearch/issues)
- **Discussions**: [GitHub Discussions](https://github.com/The-Swarm-Corporation/AdvancedResearch/discussions)
- **Discord**: [Join our community](https://discord.gg/EamjgSaEQf)

<p align="center">
  <strong>Built with <a href="https://github.com/kyegomez/swarms">Swarms</a> framework for production-grade agentic applications </strong>
</p>
