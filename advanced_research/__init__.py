"""
AdvancedResearch: Enhanced Multi-Agent Research System

An advanced implementation of the orchestrator-worker pattern from Anthropic's paper,
"How we built our multi-agent research system," achieving 90.2% performance improvement
over single-agent systems through parallel execution, LLM-as-judge evaluation, and
professional report generation.

Key Features:
- Enhanced orchestrator-worker architecture with explicit thinking processes
- Advanced web search integration with quality scoring and reliability assessment
- LLM-as-judge evaluation for research completeness and gap identification
- High-performance parallel execution with up to 5 concurrent specialized agents
- Professional citation system with intelligent source descriptions
- Export functionality with customizable paths and comprehensive metadata
- Multi-layer error recovery with fallback content generation

"""

from advanced_research.main import (
    # Main orchestrator class
    AdvancedResearch,
    # Dataclasses for system coordination
    AgentMemory,
    CitationAgent,
    CitationOutput,
    # Core agent classes
    LeadResearcherAgent,
    OrchestrationMetrics,
    ResearchStrategy,
    ResearchSubagent,
    # Pydantic data models
    SourceInfo,
    SubagentFindings,
    SubagentResult,
    SynthesisResult,
    # Utility functions
    exa_search,
)

# Package metadata
__version__ = "1.0.0"
__author__ = "The Swarm Corporation"
__description__ = "A multi-agent AI framework for collaborative scientific research, implementing tournament-based hypothesis evolution and peer review systems"


# Define what gets imported with "from advancedresearch import *"
__all__ = [
    # Primary class (most important)
    "AdvancedResearch",
    # Core agent classes
    "LeadResearcherAgent",
    "ResearchSubagent",
    "CitationAgent",
    # Data models for advanced usage
    "SourceInfo",
    "SubagentFindings",
    "ResearchStrategy",
    "SynthesisResult",
    "CitationOutput",
    "AgentMemory",
    "SubagentResult",
    "OrchestrationMetrics",
    # Utility functions
    "exa_search",
    # Package metadata
    "__version__",
    "__author__",
    "__description__",
]
