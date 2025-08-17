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
  - [Basic Research Setup](#basic-research-setup)
  - [Advanced Multi-Loop Research](#advanced-multi-loop-research)
  - [Batch Processing Setup](#batch-processing-setup)
  - [Custom Output Format](#custom-output-format)
  - [Chat Interface Setup](#chat-interface-setup)
  - [REST API Deployment](#rest-api-deployment)
  - [Mixed Mode Configuration](#mixed-mode-configuration)
- [Dependencies](#dependencies)
- [Error Handling](#error-handling)
- [Environment Variables](#environment-variables)
- [File Outputs](#file-outputs)

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
| `chat_interface` | `bool` | `False` | Whether to launch a Gradio chat interface instead of running directly |

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

#### `run(task: str = None, img: Optional[str] = None, **kwargs) -> str | None`

Executes the main research workflow for a given task. If `chat_interface=True`, launches a Gradio chat interface instead.

**Parameters:**
- `task` (str, optional): The research question or task to investigate. Not required when `chat_interface=True`
- `img` (Optional[str]): Optional image input for multimodal research (default: None)
- `**kwargs`: Additional arguments to pass to `launch_chat_interface()` when using chat interface

**Returns:**
- `str`: Formatted conversation history if `export_on=False` and `chat_interface=False`
- `None`: If `export_on=True` (results saved to JSON file) or when launching chat interface

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

#### `chat_response(message: str, history: List[List[str]]) -> str`

Processes a chat message and returns the research response for Gradio interface.

**Parameters:**
- `message` (str): The user's research question/task
- `history` (List[List[str]]): Chat history from Gradio (not used internally)

**Returns:**
- `str`: The final research response from the director agent

**Example:**
```python
# This method is typically called internally by Gradio
response = research_system.chat_response(
    "What are the latest AI developments?", 
    []
)
```

#### `create_gradio_interface() -> gr.Interface`

Creates and returns a Gradio chat interface for the research system.

**Returns:**
- `gr.Interface`: The configured Gradio ChatInterface

**Raises:**
- `ImportError`: If Gradio is not installed

**Example:**
```python
interface = research_system.create_gradio_interface()
# Now you can launch it manually
interface.launch()
```

#### `launch_chat_interface(share: bool = False, server_name: str = "127.0.0.1", server_port: int = 7860, **kwargs) -> None`

Launches the Gradio chat interface for interactive research.

**Parameters:**
- `share` (bool): Whether to create a public link. Default is False
- `server_name` (str): Server host. Default is "127.0.0.1"
- `server_port` (int): Server port. Default is 7860
- `**kwargs`: Additional arguments to pass to `gradio.launch()`

**Returns:**
- `None`: Launches the interface in blocking mode

**Example:**
```python
# Launch local interface
research_system.launch_chat_interface()

# Launch with public sharing
research_system.launch_chat_interface(
    share=True,
    server_port=8080
)
```

#### `api(host: str = "127.0.0.1", port: int = 8000, reload: bool = False, **kwargs) -> None`

Deploys the Advanced Research system as a REST API using FastAPI.

**Parameters:**
- `host` (str): Server host address. Default is "127.0.0.1"
- `port` (int): Server port. Default is 8000
- `reload` (bool): Enable auto-reload for development. Default is False
- `**kwargs`: Additional arguments to pass to `uvicorn.run()`

**Available Endpoints:**
- `GET /`: Root endpoint with API information
- `GET /health`: Health check endpoint
- `POST /research`: Conduct a single research task
- `POST /research/batch`: Conduct multiple research tasks
- `GET /research/methods`: Get available output methods
- `GET /system/info`: Get system configuration info
- `GET /docs`: Interactive API documentation (Swagger UI)
- `GET /redoc`: Alternative API documentation (ReDoc)

**Example:**
```python
# Start the API server
research_system = AdvancedResearch(name="My Research API")
research_system.api(host="0.0.0.0", port=8080)

# Make requests to the API (from another terminal/script)
import requests
response = requests.post(
    "http://localhost:8080/research",
    json={"task": "What are the latest AI trends?"}
)
print(response.json())
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
| `chat_interface` | `bool` | Flag indicating whether to use chat interface mode |

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

### `summarization_agent(model_name: str = "claude-3-7-sonnet-20250219", task: str = None, max_tokens: int = 1000, img: str = None, **kwargs) -> str`

Creates a summarization agent for generating concise summaries of research findings.

**Parameters:**
- `model_name` (str): Model to use for summarization. Default is "claude-3-7-sonnet-20250219"
- `task` (str): The summarization task
- `max_tokens` (int): Token limit for summary. Default is 1000
- `img` (str): Optional image input
- `**kwargs`: Additional keyword arguments

**Returns:**
- `str`: Generated summary

### `create_json_file(data: dict, file_name: str) -> None`

Utility function to create or update JSON files with conversation data.

**Parameters:**
- `data` (dict): Data to write to the file
- `file_name` (str): Target file name

**Returns:**
- `None`: File is created/updated on disk

## Types and Enums

### HistoryOutputType

String literal type for output formatting options:

- `"all"`: Complete conversation history with full context
- `"final"`: Only the final output from the research process
- `"json"`: JSON-formatted output
- `"markdown"`: Markdown-formatted output

### AdvancedResearchAdditionalConfig

Configuration schema for advanced research system settings:

```python
class AdvancedResearchAdditionalConfig(BaseModel):
    worker_model_name: str = "gpt-4.1"
    worker_max_tokens: int = 8000
    exa_search_num_results: int = 2
    exa_search_max_characters: int = 100
```

**Configuration Fields:**
- `worker_model_name`: Model name for worker agents
- `worker_max_tokens`: Maximum tokens for worker agent responses
- `exa_search_num_results`: Number of search results to return from Exa API
- `exa_search_max_characters`: Maximum characters per Exa search result

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

### Chat Interface Setup

```python
# Chat interface configuration
chat_system = AdvancedResearch(
    name="Interactive Research Assistant",
    description="Ask me any research question for comprehensive analysis",
    chat_interface=True,
    director_model_name="claude-3-5-sonnet-20250115",
    director_max_tokens=10000
)

# Launch the chat interface
chat_system.run()  # This will launch Gradio interface
# Or explicitly launch with custom settings
chat_system.launch_chat_interface(
    share=True,  # Create public link
    server_port=8080
)
```

### REST API Deployment

```python
# API deployment configuration
api_system = AdvancedResearch(
    name="Research API Service",
    description="REST API for automated research tasks",
    export_on=False,  # Return results directly via API
    output_type="json"
)

# Deploy as REST API
api_system.api(
    host="0.0.0.0",  # Accept external connections
    port=8000,
    reload=True  # Development mode
)

# Example API usage (from client)
import requests

# Single research task
response = requests.post(
    "http://localhost:8000/research",
    json={"task": "Latest developments in renewable energy"}
)
result = response.json()

# Batch research tasks
batch_response = requests.post(
    "http://localhost:8000/research/batch",
    json={
        "tasks": [
            "AI safety research trends",
            "Quantum computing applications",
            "Climate change solutions"
        ]
    }
)
batch_results = batch_response.json()
```

### Mixed Mode Configuration

```python
# System that supports multiple interfaces
multi_system = AdvancedResearch(
    name="Multi-Interface Research System",
    description="Supports direct calls, chat, and API",
    director_model_name="claude-3-5-sonnet-20250115",
    output_type="all",
    export_on=True
)

# Use programmatically
result = multi_system.run("Research quantum computing")

# Launch chat interface
multi_system.launch_chat_interface(server_port=7860)

# Deploy API (in separate process/script)
multi_system.api(port=8000)
```

## Dependencies

The Advanced Research System requires the following key dependencies:

### Core Dependencies
- `swarms`: Multi-agent framework
- `anthropic` or `openai`: LLM providers
- `httpx`: HTTP client for Exa API
- `pydantic`: Data validation
- `loguru`: Logging
- `orjson`: Fast JSON serialization

### Optional Dependencies
- `gradio`: For chat interface functionality
- `fastapi`: For REST API deployment
- `uvicorn`: ASGI server for API

### Installation
```bash
# Core installation
pip install advanced-research

# With chat interface support
pip install advanced-research[chat]

# With API support  
pip install advanced-research[api]

# Full installation with all features
pip install advanced-research[all]
```

## Error Handling

The system includes built-in error handling for:

- **API Failures**: Graceful handling of Exa search API errors
- **Model Errors**: Fallback mechanisms for LLM failures  
- **Network Issues**: Timeout and retry logic for external calls
- **Invalid Inputs**: Validation for required parameters

**Common Error Scenarios:**

1. **Missing API Keys**: Ensure `EXA_API_KEY` is set (required), and either `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` for LLM functionality
2. **Network Connectivity**: Check internet connection for Exa searches
3. **Model Limits**: Adjust `max_tokens` if hitting model limits
4. **Invalid Output Types**: Use only supported `HistoryOutputType` values
5. **Missing Dependencies**: Install `gradio` for chat interface or `fastapi` for API features
6. **Port Conflicts**: Ensure specified ports are available for chat/API interfaces
7. **Chat Interface Errors**: Handle Gradio-specific errors gracefully

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

# Chat interface error handling
try:
    chat_system = AdvancedResearch(chat_interface=True)
    chat_system.run()
except ImportError:
    print("Gradio not installed. Install with: pip install gradio")
except Exception as e:
    print(f"Chat interface failed: {e}")

# API deployment error handling  
try:
    api_system = AdvancedResearch()
    api_system.api(port=8000)
except ImportError:
    print("FastAPI/uvicorn not installed. Install with: pip install fastapi uvicorn")
except OSError as e:
    if "Address already in use" in str(e):
        print("Port 8000 is busy. Try a different port.")
    else:
        print(f"API deployment failed: {e}")
```

## Environment Variables

**Required Environment Variables:**

```bash
# Exa Search API Key (Required for web search functionality)
EXA_API_KEY="your_exa_api_key"
```

**Optional Environment Variables:**

```bash
# Anthropic API Key (For Claude models)
ANTHROPIC_API_KEY="your_anthropic_api_key"

# OpenAI API Key (For GPT models)
OPENAI_API_KEY="your_openai_api_key"

# Worker Agent Configuration
WORKER_MODEL_NAME="gpt-4.1"                    # Default model for worker agents
WORKER_MAX_TOKENS=8000                         # Max tokens for worker responses

# Exa Search Configuration
EXA_SEARCH_NUM_RESULTS=2                       # Number of Exa search results
EXA_SEARCH_MAX_CHARACTERS=100                  # Max characters per search result
```

**Note:** At minimum, you need `EXA_API_KEY` for web search functionality. For LLM functionality, you need either `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`.

**Setup Instructions:**
1. Copy `.env.example` to `.env`: `cp .env.example .env`
2. Edit `.env` with your actual API keys
3. Never commit `.env` files to version control

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
