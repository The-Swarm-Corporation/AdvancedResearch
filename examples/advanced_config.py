#!/usr/bin/env python3
"""
Advanced Configuration Example for Advanced Research

This example shows how to use advanced configuration options
including custom models, token limits, and multiple loops.
"""

from advanced_research import AdvancedResearch


def advanced_research():
    """Run research with advanced configuration options."""

    # Initialize with custom settings
    research_system = AdvancedResearch(
        name="Advanced Research Team",
        description="Specialized research system with advanced configuration",
        director_model_name="claude-3-5-sonnet-20250115",
        worker_model_name="claude-3-5-sonnet-20250115",
        director_max_tokens=10000,
        max_loops=2,  # Multiple research iterations
        output_type="all",  # Include full conversation history
        export_on=True,
    )

    # Run research with advanced configuration
    result = research_system.run(
        "What are the most effective treatments for Type 2 diabetes?"
    )

    return result


if __name__ == "__main__":
    advanced_research()
