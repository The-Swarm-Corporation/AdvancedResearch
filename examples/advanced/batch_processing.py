#!/usr/bin/env python3
"""
Batch Processing Example for Advanced Research

This example shows how to process multiple research tasks
in batch using the batched_run method.
"""

from advanced_research import AdvancedResearch


def batch_research():
    """Process multiple research tasks in batch."""

    # Initialize the system
    research_system = AdvancedResearch(
        name="Batch Research System",
        max_loops=1,
        export_on=True,
    )

    # Define multiple research tasks
    tasks = [
        "Latest advances in renewable energy storage",
        "Current state of autonomous vehicle technology",
        "Recent breakthroughs in cancer immunotherapy",
    ]

    # Run batch processing
    results = research_system.batched_run(tasks)

    return results


if __name__ == "__main__":
    batch_research()
