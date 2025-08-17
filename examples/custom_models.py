#!/usr/bin/env python3
"""
Custom Models Example for Advanced Research

This example shows how to configure different models
for director and worker agents.
"""

from advanced_research import AdvancedResearch


def model_configurations():
    """Demonstrate different model configuration options."""

    # Claude-based configuration
    claude_system = AdvancedResearch(
        name="Claude Research Team",
        description="Research system using Claude models",
        director_model_name="claude-3-5-sonnet-20250115",
        worker_model_name="claude-3-5-sonnet-20250115",
        director_max_tokens=8000,
        worker_max_tokens=6000,
        max_loops=1,
    )

    claude_result = claude_system.run(
        "What are the latest developments in natural language processing?"
    )

    # GPT-based configuration
    gpt_system = AdvancedResearch(
        name="GPT Research Team",
        description="Research system using GPT models",
        director_model_name="gpt-4",
        worker_model_name="gpt-4",
        director_max_tokens=8000,
        worker_max_tokens=6000,
        max_loops=1,
    )

    gpt_result = gpt_system.run(
        "What are the current trends in computer vision?"
    )

    # Mixed model configuration
    mixed_system = AdvancedResearch(
        name="Mixed Model Research Team",
        description="Research system using different models for director and workers",
        director_model_name="claude-3-5-sonnet-20250115",
        worker_model_name="gpt-4",
        director_max_tokens=10000,
        worker_max_tokens=8000,
        max_loops=1,
    )

    mixed_result = mixed_system.run(
        "What are the key challenges in robotics?"
    )

    return {
        "claude_result": claude_result,
        "gpt_result": gpt_result,
        "mixed_result": mixed_result,
    }


if __name__ == "__main__":
    model_configurations()
