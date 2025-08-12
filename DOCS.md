# Advanced Research System - API Documentation

## Table of Contents

- [Overview](#overview)
- [AdvancedResearch Class](#advancedresearch-class)
  - [Constructor Parameters](#constructor-parameters)
  - [Methods](#methods)
  - [Attributes](#attributes)
- [Utility Functions](#utility-functions)
- [Types and Enums](#types-and-enums)
- [Configuration Examples](#configuration-examples)
- [Error Handling](#error-handling)

## Overview

The Advanced Research System provides a sophisticated multi-agent research framework built on the `swarms` library. It implements an orchestrator-worker pattern where a director agent coordinates multiple specialized worker agents to conduct comprehensive research tasks.

## AdvancedResearch Class

The main class that orchestrates the entire research process.

```python
from advanced_research.main import AdvancedResearch
```

### Constructor Parameters

#### `__init__(self, **kwargs)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `str` | `generate_id()` | Unique identifier for the research session. Auto-generated with format: `AdvancedResearch-{uuid}-time-{timestamp}` |
| `name` | `str` | `"Advanced Research"` | Human-readable name for the research system or session |
| `description` | `str` | `"Advanced Research"` | Description of the research system's purpose or focus area |
| `worker_model_name` | `str` | `"claude-3-7-sonnet-20250219"` | Model name used for worker agents that execute searches |
| `director_agent_name` | `str` | `"Director-Agent"` | Name identifier for the director agent |
| `director_model_name` | `str` | `"claude-3-7-sonnet-20250219"` | Model name used for the director agent that coordinates research |
| `director_max_tokens` | `int` | `8000` | Maximum token limit for director agent responses |
| `output_type` | `HistoryOutputType` | `"all"` | Format for conversation history output. Options: `"all"`, `"json"`, `"markdown"` |
| `max_loops` | `int` | `1` | Number of research iteration loops to execute |
| `export_on` | `bool` | `False` | Whether to automatically export conversation history to JSON file |
| `director_max_loops` | `int` | `1` | Maximum number of loops for the director agent execution |

**Example:**
```python
research_system = AdvancedResearch(
    name="Medical Research Team",
    description="Specialized medical research focusing on diabetes treatments",
    director_model_name="claude-3-5-sonnet-20250115",
    worker_model_name="claude-3-5-sonnet-20250115", 
    director_max_tokens=10000,
    max_loops=2,
    output_type="all",
    export_on=True
)
```

### Methods

#### `run(task: str, img: Optional[str] = None) -> str | None`

Executes the main research workflow for a given task.

**Parameters:**
- `task` (str): The research question or task to investigate
- `img` (Optional[str]): Optional image input for multimodal research (default: None)

**Returns:**
- `str`: Formatted conversation history if `export_on=False`
- `None`: If `export_on=True` (results saved to JSON file)

**Example:**
```python
# Get results directly
result = research_system.run(
    "What are the latest developments in quantum computing?",
    img=None
)
print(result)

# Or with export enabled (no return value)
research_system.export_on = True
research_system.run("What are the latest developments in quantum computing?")
# Results saved to timestamped JSON file
```

#### `step(task: Optional[str], img: Optional[str] = None) -> str`

Executes a single research step using the director agent.

**Parameters:**
- `task` (Optional[str]): The research task to execute
- `img` (Optional[str]): Optional image input

**Returns:**
- `str`: Output from the director agent for this step

**Example:**
```python
step_result = research_system.step(
    "Analyze the current state of AI in healthcare"
)
```

#### `batched_run(tasks: List[str]) -> None`

Processes multiple research tasks in sequence.

**Parameters:**
- `tasks` (List[str]): List of research questions to process

**Returns:**
- `None`: All results are processed according to the `export_on` setting

**Example:**
```python
tasks = [
    "Latest advances in renewable energy storage",
    "Current state of autonomous vehicle technology", 
    "Recent breakthroughs in cancer immunotherapy"
]
research_system.batched_run(tasks)
```

#### `get_output_methods() -> list`

Returns the available output formatting options.

**Returns:**
- `list`: List of available `HistoryOutputType` values

**Example:**
```python
available_formats = research_system.get_output_methods()
print(f"Available formats: {available_formats}")
# Output: Available formats: ['all', 'json', 'markdown']
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Unique session identifier |
| `name` | `str` | Research system name |
| `description` | `str` | System description |
| `worker_model_name` | `str` | Model used by worker agents |
| `director_agent_name` | `str` | Director agent identifier |
| `director_model_name` | `str` | Model used by director agent |
| `director_max_tokens` | `int` | Token limit for director |
| `output_type` | `HistoryOutputType` | Output format type |
| `max_loops` | `int` | Number of research loops |
| `export_on` | `bool` | Export enablement flag |
| `director_max_loops` | `int` | Director loop limit |
| `conversation` | `Conversation` | Swarms conversation object for history tracking |

## Utility Functions

### `generate_id() -> str`

Generates a unique identifier for research sessions.

**Returns:**
- `str`: Unique ID in format `AdvancedResearch-{uuid4}-time-{timestamp}`

### `exa_search(query: str) -> str`

Executes web search using the Exa.ai API.

**Parameters:**
- `query` (str): Natural language search query

**Returns:**
- `str`: JSON-formatted search results with summaries and insights

**Example:**
```python
results = exa_search("Latest developments in quantum computing 2024")
```

### `execute_worker_search_agents(queries: List[str]) -> str`

Runs multiple worker agents in parallel using ThreadPoolExecutor.

**Parameters:**
- `queries` (List[str]): List of search queries to execute

**Returns:**
- `str`: Combined results from all worker agents

### `create_director_agent(**kwargs) -> str`

Creates and runs a director agent for research coordination.

**Parameters:**
- `agent_name` (str): Name for the director agent
- `model_name` (str): Model to use
- `task` (str): Research task
- `max_tokens` (int): Token limit
- `img` (Optional[str]): Image input
- `max_loops` (int): Loop limit

**Returns:**
- `str`: Director agent output

## Types and Enums

### HistoryOutputType

String literal type for output formatting options:

- `"all"`: Complete conversation history with full context
- `"json"`: JSON-formatted output
- `"markdown"`: Markdown-formatted output

## Configuration Examples

### Basic Research Setup

```python
from advanced_research.main import AdvancedResearch

# Simple setup
research_system = AdvancedResearch(
    name="Basic Research",
    max_loops=1
)

result = research_system.run("What is machine learning?")
```

### Advanced Multi-Loop Research

```python
# Advanced configuration
research_system = AdvancedResearch(
    name="Deep Research System",
    description="Multi-loop comprehensive research",
    director_model_name="claude-3-5-sonnet-20250115",
    worker_model_name="claude-3-5-sonnet-20250115",
    max_loops=3,
    director_max_loops=2,
    director_max_tokens=12000,
    output_type="all",
    export_on=True
)

research_system.run("Comprehensive analysis of AI safety research")
```

### Batch Processing Setup

```python
# Batch processing configuration
batch_system = AdvancedResearch(
    name="Batch Research Processor",
    output_type="json",
    export_on=True,
    max_loops=1
)

research_topics = [
    "Climate change mitigation strategies",
    "Renewable energy adoption rates",
    "Carbon capture technologies"
]

batch_system.batched_run(research_topics)
```

### Custom Output Format

```python
# Custom output formatting
custom_system = AdvancedResearch(
    name="Custom Output System",
    output_type="markdown",
    export_on=False  # Get results directly
)

markdown_result = custom_system.run("Benefits of renewable energy")
print(markdown_result)
```

## Error Handling

The system includes built-in error handling for:

- **API Failures**: Graceful handling of Exa search API errors
- **Model Errors**: Fallback mechanisms for LLM failures  
- **Network Issues**: Timeout and retry logic for external calls
- **Invalid Inputs**: Validation for required parameters

**Common Error Scenarios:**

1. **Missing API Keys**: Ensure `EXA_API_KEY` and `ANTHROPIC_API_KEY` are set
2. **Network Connectivity**: Check internet connection for Exa searches
3. **Model Limits**: Adjust `max_tokens` if hitting model limits
4. **Invalid Output Types**: Use only supported `HistoryOutputType` values

**Example Error Handling:**

```python
try:
    research_system = AdvancedResearch(
        name="Error-Safe Research",
        export_on=True
    )
    
    result = research_system.run("Complex research query")
    
except Exception as e:
    print(f"Research failed: {e}")
    # Implement fallback or retry logic
```

## Environment Variables

Required environment variables:

```bash
# Required
ANTHROPIC_API_KEY="your_anthropic_api_key"
EXA_API_KEY="your_exa_api_key"

# Optional  
OPENAI_API_KEY="your_openai_api_key"
```

## File Outputs

When `export_on=True`, the system generates JSON files with:

- **Filename Pattern**: `{session_id}.json`
- **Content**: Complete conversation history with timestamps
- **Location**: Current working directory
- **Format**: Structured JSON with message history

**Example Output File**: `AdvancedResearch-abc123-time-20240315143022.json`

```json
[
    {
        "role": "human",
        "content": "What are the latest developments in quantum computing?",
        "timestamp": "2024-03-15T14:30:22Z"
    },
    {
        "role": "assistant", 
        "content": "Based on comprehensive research...",
        "timestamp": "2024-03-15T14:32:15Z"
    }
]
```
