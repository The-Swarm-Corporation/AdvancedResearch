#!/usr/bin/env python3
"""
Export Example for Advanced Research

This example shows how to use the export functionality to save
research results to JSON files.
"""

from advanced_research import AdvancedResearch


def export_research():
    """Run research with export functionality enabled."""

    # Initialize with export enabled
    research_system = AdvancedResearch(
        name="Export Research Team",
        description="Research team with export capabilities",
        max_loops=1,
        export_on=True,  # Enable JSON export
    )

    # Run research - will automatically export to JSON file
    result = research_system.run(
        "What are the latest developments in renewable energy?"
    )

    return result


if __name__ == "__main__":
    export_research()
