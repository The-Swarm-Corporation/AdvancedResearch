#!/usr/bin/env python3
"""
Output Formats Example for Advanced Research

This example shows how to use different output format options
including JSON, markdown, and full conversation history.
"""

from advanced_research import AdvancedResearch


def format_examples():
    """Demonstrate different output format options."""

    # JSON output format
    json_system = AdvancedResearch(
        name="JSON Research System",
        output_type="json",
        export_on=False,
    )

    json_result = json_system.run(
        "What are the key challenges in AGI development?"
    )

    # Markdown output format
    markdown_system = AdvancedResearch(
        name="Markdown Research System",
        output_type="markdown",
        export_on=False,
    )

    markdown_result = markdown_system.run(
        "What are the latest developments in quantum cryptography?"
    )

    # Full conversation history
    full_system = AdvancedResearch(
        name="Full History Research System",
        output_type="all",
        export_on=False,
    )

    full_result = full_system.run(
        "What are the current trends in machine learning?"
    )

    # Get available output methods
    available_formats = full_system.get_output_methods()

    return {
        "json_result": json_result,
        "markdown_result": markdown_result,
        "full_result": full_result,
        "available_formats": available_formats,
    }


if __name__ == "__main__":
    format_examples()
