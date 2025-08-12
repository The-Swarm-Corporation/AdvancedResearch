#!/usr/bin/env python3
"""
API Demo for Advanced Research

This script demonstrates how to deploy the Advanced Research system as a REST API.
Simply run this script to launch a FastAPI server with comprehensive research endpoints.
"""

from advanced_research.main import AdvancedResearch


def main():
    """Launch the Advanced Research API server."""

    # Initialize the research system with API-optimized configuration
    research_system = AdvancedResearch(
        name="🔬 Advanced Research API",
        description="REST API for the Advanced Research multi-agent system. Conduct comprehensive research through HTTP endpoints.",
        max_loops=1,
        output_type="final",  # Use final output for API responses
        export_on=False,  # Disable auto-export in API mode
        chat_interface=False,  # API mode
    )

    # Deploy the API
    research_system.api(
        host="127.0.0.1",
        port=8000,
        reload=True,  # Enable auto-reload for development
    )


if __name__ == "__main__":
    main()
