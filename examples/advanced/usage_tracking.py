#!/usr/bin/env python3
"""
Usage Tracking Example for Advanced Research

Shows how to inspect input/output tokens and attribute cost across
Swarms API agent calls and Exa searches after a research run.
"""

import json

from advanced_research import AdvancedResearch


def usage_tracking():
    """Run research, then print token and cost usage."""

    research = AdvancedResearch(
        name="Usage Tracking Demo",
        description="Demonstrates get_usage() for Swarms + Exa cost attribution",
        director_model_name="gpt-5.5",
        worker_model_name="gpt-5.4-mini",
        max_loops=1,
        verbose=False,
    )

    report = research.run(
        "What are the latest developments in solid-state batteries?"
    )

    usage = research.get_usage()

    print("=== Report (truncated) ===")
    print((report[:500] + "...") if len(report) > 500 else report)
    print()

    print("=== Usage summary ===")
    print(
        json.dumps(
            {
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
                "total_tokens": usage["total_tokens"],
                "swarms_calls": usage["swarms_calls"],
                "swarms_cost_usd": usage["swarms_cost_usd"],
                "exa_searches": usage["exa_searches"],
                "exa_results": usage["exa_results"],
                "exa_cost_usd": usage["exa_cost_usd"],
                "total_cost_usd": usage["total_cost_usd"],
            },
            indent=2,
        )
    )
    print()
    print(f"research.total_cost == {research.total_cost}")
    print()

    print("=== Per-call attribution ===")
    for call in usage["calls"]:
        if call["service"] == "swarms":
            print(
                f"[swarms] {call.get('agent_name')} "
                f"({call.get('stage')}) "
                f"in={call['input_tokens']} out={call['output_tokens']} "
                f"cost=${call['total_cost']:.6f}"
            )
        else:
            print(
                f"[exa] type={call.get('search_type')} "
                f"results={call.get('num_results_returned')}/"
                f"{call.get('num_results_requested')} "
                f"cost=${call['total_cost']:.6f} "
                f"query={call.get('query')!r}"
            )

    return {"report": report, "usage": usage}


if __name__ == "__main__":
    usage_tracking()
