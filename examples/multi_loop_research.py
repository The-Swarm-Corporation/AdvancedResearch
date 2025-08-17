#!/usr/bin/env python3
"""
Multi-Loop Research Example for Advanced Research

This example shows how to use multiple research loops
for iterative refinement and deeper investigation.
"""

from advanced_research import AdvancedResearch


def iterative_research():
    """Run research with multiple loops for iterative refinement."""

    # Initialize with multiple loops
    research_system = AdvancedResearch(
        name="Iterative Research Team",
        description="Research system with iterative refinement capabilities",
        max_loops=3,  # Three research iterations
        director_max_tokens=12000,
        worker_max_tokens=8000,
        output_type="all",  # Include full conversation history
        export_on=True,
    )

    # Run iterative research
    result = research_system.run(
        "What are the most promising approaches to achieving AGI?"
    )

    return result


def step_by_step_research():
    """Demonstrate step-by-step research execution."""

    # Initialize the system
    research_system = AdvancedResearch(
        name="Step-by-Step Research Team",
        description="Research system with step-by-step execution",
        max_loops=2,
        export_on=False,
    )

    # First research step
    step1_result = research_system.run(
        "What are the current limitations of large language models?"
    )

    # Second research step (builds on first)
    step2_result = research_system.run(
        "How can we overcome these limitations?"
    )

    return {"step1": step1_result, "step2": step2_result}


if __name__ == "__main__":
    iterative_research()
    step_by_step_research()
