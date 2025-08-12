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
    AdvancedResearch,
    execute_worker_search_agents,
)

__all__ = [
    "AdvancedResearch",
    "execute_worker_search_agents",
]
