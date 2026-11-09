#!/usr/bin/env python3
"""
Basic Usage Example for Advanced Research

This example shows the simplest way to use the AdvancedResearch system
for basic research queries.
"""

from advanced_research import AdvancedResearch


def basic_research():
    """Run basic research with minimal configuration."""

    # Initialize the research system
    research_system = AdvancedResearch(
        name="Basic Research Team",
        description="Simple research system for basic queries",
        max_loops=1,
    )

    # Run research and get results
    result = research_system.run(
        "What are the latest developments in quantum computing?"
    )

    return result


if __name__ == "__main__":
    basic_research()
