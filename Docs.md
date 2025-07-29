# Advanced Research System Documentation

## Table of Contents

1.  [Overview](#overview)
2.  [Architecture](#architecture)
3.  [Installation](#installation)
4.  [Quick Start](#quick-start)
5.  [API Reference](#api-reference)
6.  [Agent System](#agent-system)
7.  [Configuration](#configuration)
8.  [Advanced Usage](#advanced-usage)
9.  [Examples](#examples)
10. [Export Functionality](#export-functionality)
11. [Troubleshooting](#troubleshooting)
12. [Citation](#citation)

## Overview

This is an implementation of the advanced multi-agent research system based on Anthropic's paper, ["How we built our multi-agent research system."](https://www.anthropic.com/news/how-we-built-our-multi-agent-research-system) It is built using the `swarms` framework and operationalizes the orchestrator-worker pattern for complex, open-ended research tasks with enhanced parallel execution capabilities.

The system uses a `LeadResearcherAgent` to decompose high-level research queries into parallelizable sub-tasks. These tasks are executed concurrently by specialized `ResearchSubagent` workers equipped with real web search tools. The findings are iteratively synthesized and refined through LLM-as-judge evaluation, and a final, professionally cited report is generated with optional export functionality.

### Key Features

-   **Enhanced Orchestrator-Worker Architecture**: A `LeadResearcherAgent` with advanced thinking processes plans and synthesizes, while ephemeral `ResearchSubagent` workers execute focused research tasks with iterative search capabilities.
-   **Real-Time Web Search Integration**: Utilizes `exa_search` for real-time, relevant web searches with quality scoring and source reliability assessment.
-   **LLM-as-Judge Evaluation**: Advanced progress evaluation system that determines research completeness and identifies missing topics for targeted follow-up research.
-   **Parallel Research Execution**: Leverages `ThreadPoolExecutor` to run up to 5 specialized agents concurrently, achieving 90% time reduction for complex queries.
-   **Professional Citation System**: A specialized `CitationAgent` processes the final report with enhanced source descriptions and academic-style citations.
-   **Export Functionality**: Built-in report export to Markdown files with customizable file paths and automatic timestamping.
-   **Adaptive Error Handling**: Multi-layer error recovery with fallback content generation and emergency report creation.
-   **Advanced Memory Management**: Comprehensive state persistence with conversation history and orchestration metrics tracking.

## Architecture

The system follows a dynamic, multi-phase workflow orchestrated by the `LeadResearcherAgent` with enhanced coordination capabilities.

```
                [User Query + Export Options]
                            │
                            ▼
           ┌─────────────────────────────────┐
           │    LeadResearcherAgent          │ (Enhanced Orchestrator)
           │  - Query Analysis & Planning    │
           │  - LLM-as-Judge Evaluation      │
           │  - Iterative Strategy Refinement│
           └─────────────────────────────────┘
                            │ 1. Analyze & Decompose (with thinking process)
                            ▼
       ┌─────────────────────────────────────────┐
       │         Parallel Sub-Tasks              │
       │      (Up to 5 concurrent tasks)         │
       └─────────────────────────────────────────┘
          │           │           │           │
          ▼           ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │SubAgent 1│ │SubAgent 2│ │SubAgent 3│ │SubAgent N│ (Specialized Workers)
    │Multi-loop│ │Multi-loop│ │Multi-loop│ │Multi-loop│
    │ Search   │ │ Search   │ │ Search   │ │ Search   │
    └──────────┘ └──────────┘ └──────────┘ └──────────┘
          │           │           │           │
          ▼           ▼           ▼           ▼
       ┌─────────────────────────────────────────┐
       │     Enhanced Results Aggregation        │
       │  - Quality Assessment & Confidence      │
       │  - Source Deduplication & Scoring       │
       └─────────────────────────────────────────┘
                            │ 2. Synthesis & LLM-as-Judge Evaluation
                            ▼
           ┌─────────────────────────────────┐
           │    LeadResearcherAgent          │
           │  - Completeness Assessment      │
           │  - Gap Identification           │
           │  - Iterative Refinement         │
           └─────────────────────────────────┘
                            │ 3. Generate Final Report
                            ▼
           ┌─────────────────────────────────┐
           │      Enhanced CitationAgent     │ (Post-Processor)
           │  - Smart Source Descriptions    │
           │  - Professional Citations       │
           │  - Quality Assurance            │
           └─────────────────────────────────┘
                            │ 4. Export & Delivery
                            ▼
              [Final Cited Report + Optional Export]
```

### Workflow Process

1.  **Enhanced Planning Phase**: The `LeadResearcherAgent` analyzes the user's query with explicit thinking processes and decomposes it into specific, searchable sub-tasks with priority scoring.
2.  **Parallel Research Phase**: Multiple `ResearchSubagent` workers are dynamically created with up to 3 iterative search loops each, executing research concurrently using advanced `exa_search` capabilities.
3.  **LLM-as-Judge Evaluation**: The `LeadResearcherAgent` employs sophisticated evaluation methodology to assess research completeness, identify gaps, and determine if additional iterations are needed.
4.  **Enhanced Citation Processing**: The `CitationAgent` processes the final report with intelligent source descriptions, professional formatting, and quality assessment.
5.  **Export & Delivery**: Optional export functionality saves the final report to customizable Markdown files with comprehensive metadata.

## Installation

### Prerequisites

-   Python 3.10 or higher
-   API keys for Claude (Anthropic) and Exa search
-   `uv` package manager (recommended) or pip

### Install Dependencies with uv (Recommended)

The `AdvancedResearch` system is built using the `swarms` framework. Using `uv` provides faster, more reliable dependency management:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv add swarms
uv add python-dotenv requests loguru pydantic
```

### Alternative Installation with pip

```bash
pip install -U swarms
pip install python-dotenv requests loguru pydantic
```

### Environment Setup

Create a `.env` file in your project root with your API keys:

```bash
# Claude API Key (Primary LLM)
ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Exa Search API Key
EXA_API_KEY="your_exa_api_key_here"

# Optional: OpenAI API Key (alternative LLM)
OPENAI_API_KEY="your_openai_api_key_here"
```

## Quick Start

### Basic Usage

Save the implementation code as `advanced_research.py` and run it:

```python
from advanced_research import AdvancedResearch

# Initialize the advanced research system
research_system = AdvancedResearch(
    model_name="claude-3-7-sonnet-20250219",  # Default high-performance model
    max_iterations=3,
    max_workers=5,
    enable_parallel_execution=True,
    memory_optimization=True
)

# Define your research goal
research_query = (
    "What are the benefits and risks of using AI in healthcare, "
    "and what are the primary ethical considerations?"
)

# Run the research workflow with export
results = research_system.research(
    research_query, 
    export=True, 
    export_path="healthcare_ai_report.md"
)

# Print the final, cited report
print("\n" + "="*60)
print("           ADVANCED RESEARCH SYSTEM RESULTS")
print("="*60 + "\n")
print(results["final_report"])

# Access comprehensive results
print(f"\nResearch Strategy: {results['research_strategy']['strategy_type']}")
print(f"Agents Spawned: {results['execution_metrics']['agents_spawned']}")
print(f"Total Sources: {results['source_analysis']['total_sources']}")
print(f"Synthesis Quality: {results['execution_metrics']['synthesis_quality']:.2f}")
```

## API Reference

### `AdvancedResearch` Class

#### Constructor

```python
AdvancedResearch(
    model_name: str = "claude-3-7-sonnet-20250219",
    max_iterations: int = 3,
    max_workers: int = 5,
    base_path: str = "agent_workspace",
    enable_parallel_execution: bool = True,
    memory_optimization: bool = True
)
```

**Parameters:**
-   `model_name`: The LLM model for all agents (default: Claude Sonnet 3.5)
-   `max_iterations`: Maximum synthesis-refinement loops with LLM-as-judge evaluation
-   `max_workers`: Maximum number of concurrent `ResearchSubagent` workers
-   `base_path`: Directory for persistent agent state files
-   `enable_parallel_execution`: Enable/disable parallel agent execution
-   `memory_optimization`: Enable advanced memory management features

#### Methods

##### `research(query: str, export: bool = False, export_path: str = None) -> Dict[str, Any]`

The main entry point for the complete research workflow with enhanced capabilities.

**Parameters:**
-   `query`: The research question or topic to investigate
-   `export`: Whether to export the final report to a file
-   `export_path`: Custom file path for export (optional, auto-generates if None)

**Returns:** A comprehensive dictionary containing:
- `final_report`: The complete cited research report
- `research_strategy`: Strategy analysis and complexity assessment
- `execution_metrics`: Performance metrics and timing data
- `source_analysis`: Source quality and citation statistics  
- `subagent_results`: Detailed subagent performance data
- `research_metadata`: System information and export details

##### `export_report(report_content: str, file_path: str = None) -> str`

Standalone method to export any report content to a Markdown file.

**Parameters:**
-   `report_content`: The content to export
-   `file_path`: Custom file path (optional, auto-generates timestamp-based name)

**Returns:** The path where the file was saved

### Enhanced Data Structures

#### `SubagentResult` Dataclass

```python
@dataclass
class SubagentResult:
    agent_id: str
    task_assignment: str
    research_findings: str
    source_collection: List[Dict[str, Any]]
    execution_time: float
    error_status: Optional[str]
    confidence_metrics: Dict[str, float]
    parallel_tool_usage: List[str]
    completion_timestamp: str
```

#### `ResearchStrategy` Model

```python
class ResearchStrategy(BaseModel):
    strategy_type: str  # "focused", "breadth_first", or "iterative_depth"
    complexity_score: int  # 1-10 complexity assessment
    subtasks: List[str]  # Decomposed research tasks
    priority_matrix: List[int]  # Task priority scores
    estimated_duration: float  # Estimated completion time
```

## Agent System

### LeadResearcherAgent (Enhanced Orchestrator)

The central orchestrator with advanced reasoning capabilities and explicit thinking processes:

**Key Capabilities:**
1.  **Strategic Planning**: Advanced query analysis with complexity assessment and thinking process documentation
2.  **LLM-as-Judge Evaluation**: Sophisticated progress evaluation with detailed reasoning and gap identification
3.  **Adaptive Management**: Dynamic strategy refinement based on intermediate results and identified gaps
4.  **Memory Management**: Comprehensive state tracking and conversation history

**Thinking Process:** Each decision includes explicit reasoning blocks that are logged for transparency and debugging.

### ResearchSubagent (Specialized Worker)

Enhanced worker agents with iterative search capabilities:

**Key Features:**
-   **Multi-Loop Search**: Up to 3 iterative search cycles per task
-   **Quality Assessment**: Source evaluation with reliability scoring
-   **Strategic Search Progression**: Broad → Targeted → Specific search patterns
-   **Confidence Metrics**: Self-assessment of research quality and coverage

**Search Strategy:**
1. **Phase 1 - Initial Exploration**: Broad context searches
2. **Phase 2 - Targeted Refinement**: Focused investigation based on initial findings  
3. **Phase 3 - Final Synthesis**: Comprehensive result compilation

### CitationAgent (Enhanced Post-Processor)

Professional citation processing with intelligent source handling:

**Enhanced Features:**
-   **Smart Source Descriptions**: Automatic content type inference from URLs
-   **Quality-Based Formatting**: Citation styling based on source reliability
-   **Fallback Content Generation**: Meaningful descriptions when source content is unavailable
-   **Academic Standards**: Professional reference formatting

## Configuration

### Environment Variables

Your API keys must be available as environment variables. Create a `.env` file:

```bash
# Primary LLM Provider (Claude recommended)
ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Search Tool API Key
EXA_API_KEY="your_exa_api_key_here"

# Alternative LLM Provider (Optional)
OPENAI_API_KEY="your_openai_api_key_here"
```

### Model Selection

The system is optimized for high-capability models. Recommended options:

```python
# High performance (recommended)
system = AdvancedResearch(model_name="claude-3-7-sonnet-20250219")

# Alternative models
system = AdvancedResearch(model_name="gpt-4o")
system = AdvancedResearch(model_name="claude-3-opus-20240229")
```

## Advanced Usage

### Customizing Research Depth and Breadth

```python
# Quick overview research
quick_system = AdvancedResearch(
    max_iterations=1,
    max_workers=3,
    enable_parallel_execution=True
)

# Deep comprehensive investigation  
deep_system = AdvancedResearch(
    max_iterations=5,
    max_workers=8,
    enable_parallel_execution=True,
    memory_optimization=True
)

# Sequential processing for debugging
debug_system = AdvancedResearch(
    max_iterations=2,
    max_workers=3,
    enable_parallel_execution=False  # Run agents sequentially
)
```

### Advanced Export Options

```python
# Basic export with auto-generated filename
results = research_system.research(query, export=True)

# Custom export path
results = research_system.research(
    query, 
    export=True, 
    export_path="reports/custom_research_2024.md"
)

# Standalone export of any content
export_path = research_system.export_report(
    content, 
    "analysis/final_report.md"
)
```

### Accessing Comprehensive Results

```python
results = research_system.research(research_query, export=True)

# Research strategy analysis
strategy = results["research_strategy"]
print(f"Strategy: {strategy['strategy_type']}")
print(f"Complexity: {strategy['complexity_score']}/10")

# Execution performance metrics
metrics = results["execution_metrics"]
print(f"Total Time: {metrics['total_time']:.2f}s")
print(f"Parallel Efficiency: {metrics['parallel_efficiency']:.1%}")
print(f"Synthesis Quality: {metrics['synthesis_quality']:.2f}")

# Source analysis
sources = results["source_analysis"] 
print(f"Sources Found: {sources['total_sources']}")
print(f"Average Quality: {sources['average_quality']:.2f}")

# Individual subagent performance
for result in results["subagent_results"]:
    print(f"Agent {result['agent_id']}: {result['confidence']:.2f} confidence")
```

## Examples

### Healthcare AI Research

```python
from advanced_research import AdvancedResearch

research_system = AdvancedResearch(
    model_name="claude-3-7-sonnet-20250219",
    max_iterations=3,
    max_workers=5
)

results = research_system.research(
    "What are the current regulatory frameworks for AI in medical diagnostics?",
    export=True,
    export_path="ai_medical_regulations.md"
)

print(f"Research completed in {results['execution_metrics']['total_time']:.1f}s")
print(f"Found {results['source_analysis']['total_sources']} sources")
```

### Financial Technology Analysis

```python
results = research_system.research(
    "How is blockchain technology being integrated into traditional banking systems?",
    export=True
)

# Access specific findings
for i, subagent in enumerate(results["subagent_results"], 1):
    print(f"\n--- Finding {i} ---")
    print(f"Task: {subagent['task']}")
    print(f"Confidence: {subagent['confidence']:.2f}")
```

## Export Functionality

### File Formats and Structure

The system exports professional Markdown reports with:

- **Executive Summary**: Research overview with methodology
- **Detailed Findings**: Organized research results with confidence indicators
- **Professional Citations**: Academic-style references with quality indicators
- **Metadata**: Research strategy, performance metrics, and system information

### Export File Structure

```markdown
# Advanced Research Report: [Query]

## Executive Summary
[Methodology and overview]

## Research Findings

### 🔥 Finding 1: [High Confidence]
[Detailed research content]

### 📊 Finding 2: [Moderate Confidence]  
[Research content with confidence note]

## References

[1] [URL] [Quality Indicator]
    Summary: [Intelligent source description]

[2] [URL] [Quality Indicator]
    Summary: [Content preview or inferred description]
```

### Export Best Practices

```python
# Organized export with directory structure
import os
os.makedirs("research_reports/2024", exist_ok=True)

results = research_system.research(
    query,
    export=True,
    export_path="research_reports/2024/ai_healthcare_analysis.md"
)

# Batch processing with timestamped exports
queries = [
    "AI ethics in healthcare",
    "Blockchain in finance", 
    "Quantum computing applications"
]

for query in queries:
    results = research_system.research(query, export=True)
    print(f"Exported: {results['research_metadata']['exported_to']}")
```

## Troubleshooting

### Common Issues

#### 1. API Key Configuration

**Problem:** `AuthenticationError` or missing API key messages
**Solution:** 
- Verify `.env` file location and format
- Check API key validity and quotas
- Ensure proper environment variable loading

```python
import os
from dotenv import load_dotenv

load_dotenv()
print("API Keys loaded:", bool(os.getenv("ANTHROPIC_API_KEY")))
```

#### 2. Export Failures

**Problem:** Export functionality not working
**Solution:**
- Check file path permissions and directory existence
- Verify disk space availability
- Use absolute paths for custom export locations

```python
# Debug export issues
try:
    results = research_system.research(query, export=True)
    print(f"Export successful: {results['research_metadata']['exported_to']}")
except Exception as e:
    print(f"Export failed: {e}")
```

#### 3. Subagent Response Parsing

**Problem:** JSON parsing errors from subagents
**Solution:**
- The system includes robust fallback parsing
- Check model selection (higher capability models recommended)
- Review logs for specific parsing errors

#### 4. Search Tool Integration

**Problem:** Exa search failures
**Solution:**
- Verify `EXA_API_KEY` configuration
- Check API rate limits and quotas
- Monitor search tool response logs

#### 5. Performance Issues

**Problem:** Slow execution or timeouts
**Solution:**
- Reduce `max_workers` for resource-constrained environments
- Disable parallel execution for debugging: `enable_parallel_execution=False`
- Adjust `max_iterations` based on query complexity

```python
# Performance-optimized configuration
performance_system = AdvancedResearch(
    max_iterations=2,
    max_workers=3,
    enable_parallel_execution=True,
    memory_optimization=True
)
```

### Debug Mode

```python
# Enable detailed logging for troubleshooting
import logging
logging.basicConfig(level=logging.DEBUG)

research_system = AdvancedResearch(
    model_name="claude-3-7-sonnet-20250219",
    enable_parallel_execution=False  # Sequential for easier debugging
)
```

## Citation

If you use this work in your research, please cite both the original paper and the `swarms` software implementation:

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

@software{advanced_research_implementation,
    title={Advanced Research System: Enhanced Multi-Agent Research Implementation},
    year={2024},
    note={Implementation based on Anthropic's multi-agent research system paper}
}
```