#!/usr/bin/env python3
"""
Chat Interface Demo for Advanced Research

This script demonstrates how to use the new Gradio chat interface feature.
Simply run this script to launch an interactive web-based chat interface
for the Advanced Research system.
"""

from advanced_research.main import AdvancedResearch


def main():
    """Launch the Advanced Research chat interface."""

    # Initialize the research system with chat interface enabled
    research_system = AdvancedResearch(
        name="🔬 Advanced Research Chat Interface",
        description="Interactive research assistant powered by advanced AI agents. Ask any research question and get comprehensive findings from multiple specialized agents.",
        max_loops=1,
        export_on=False,  # Disable export in chat mode for better performance
        chat_interface=True,  # Enable the Gradio chat interface
    )

    # Launch the chat interface
    # You can customize the launch parameters:
    research_system.run(
        share=False,  # Set to True to create a public link
        server_name="127.0.0.1",
        server_port=7860,
        # Additional Gradio launch parameters can be added here
    )


if __name__ == "__main__":
    main()
