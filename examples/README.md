# Advanced Research Examples

Examples are grouped by category. Each script is self-contained and runnable.

## Layout

```
examples/
├── basic/             # Getting started
├── configuration/     # Models, tokens, output formats
├── advanced/          # Batch, multi-loop, sessions
├── use_cases/         # Domain-specific demos
└── outputs/           # JSON exports when export_on=True
```

## Basic

| Example | Description |
|---------|-------------|
| [`basic/basic_usage.py`](basic/basic_usage.py) | Simple research with minimal configuration |
| [`basic/export_example.py`](basic/export_example.py) | Save research results to JSON |
| [`basic/chat_demo.py`](basic/chat_demo.py) | Interactive chat interface demo |

## Configuration

| Example | Description |
|---------|-------------|
| [`configuration/advanced_config.py`](configuration/advanced_config.py) | Custom models, tokens, and multiple loops |
| [`configuration/custom_models.py`](configuration/custom_models.py) | Different director/worker model setups |
| [`configuration/output_formats.py`](configuration/output_formats.py) | JSON, markdown, and conversation history |

## Advanced

| Example | Description |
|---------|-------------|
| [`advanced/batch_processing.py`](advanced/batch_processing.py) | Process multiple queries in batch |
| [`advanced/multi_loop_research.py`](advanced/multi_loop_research.py) | Iterative research with refinement |
| [`advanced/session_management.py`](advanced/session_management.py) | Session tracking and conversation management |
| [`advanced/usage_tracking.py`](advanced/usage_tracking.py) | Tokens and Swarms/Exa cost via `get_usage()` |

## Use Cases

| Example | Description |
|---------|-------------|
| [`use_cases/financial_example.py`](use_cases/financial_example.py) | Financial / investment research demo |

## Quick Start

```bash
# Prerequisites: pip install advanced-research
# Set SWARMS_API_KEY and EXA_API_KEY in .env

python examples/basic/basic_usage.py
python examples/basic/export_example.py
python examples/configuration/advanced_config.py
python examples/advanced/batch_processing.py
python examples/advanced/usage_tracking.py
python examples/use_cases/financial_example.py
```

## Prerequisites

1. **Installed the package**: `pip install advanced-research`
2. **API keys** in the environment or `.env`:
   - `SWARMS_API_KEY` — every agent runs on the Swarms API
   - `EXA_API_KEY` — web search for the subagents

## Notes

- Examples are designed to run independently
- Models and token limits are set on `AdvancedResearch(...)`, not via env vars
- With `export_on=True`, results are written under `examples/outputs/`
- Use `verbose=True` to print every agent reply to the console
