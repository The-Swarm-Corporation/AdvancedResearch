"""
Simple test script for the AdvancedResearch system with Pydantic models.
"""

import os
import sys
from pathlib import Path

from advanced_research.main import (
    AdvancedResearch,
    SubagentFindings,
    SourceInfo,
)


def test_pydantic_models():
    """Test that Pydantic models work correctly."""
    print("🧪 Testing Pydantic models...")

    # Test SourceInfo model
    source = SourceInfo(source="https://example.com", content="Test content")
    print(f"✅ SourceInfo model: {source.source}")

    # Test SubagentFindings model
    findings = SubagentFindings(
        findings="Test findings about AI in healthcare", sources=[source]
    )
    print(f"✅ SubagentFindings model: {len(findings.sources)} sources")

    print("✅ All Pydantic models working correctly!\n")


def test_simple_research():
    """Test a simple research query with reduced complexity."""
    print("🔬 Testing simplified research system...")

    # Create research system with minimal settings
    research_system = AdvancedResearch(
        model_name="claude-3-7-sonnet-20250219",
        max_iterations=1,  # Reduced to 1 for quick test
        max_workers=2,  # Reduced workers
        enable_parallel_execution=True,
        memory_optimization=True,
    )

    # Simple test query
    test_query = "What are the main benefits of AI in healthcare?"

    print(f"🔍 Testing query: '{test_query}'")
    print("⏳ Running research (this may take a moment)...\n")

    try:
        result = research_system.research(test_query)

        print("=" * 60)
        print("📊 RESEARCH RESULTS:")
        print("=" * 60)
        print(f"✅ Final report generated: {len(result['final_report'])} characters")
        print(f"✅ Sources found: {result.get('source_analysis', {}).get('total_sources', 0)}")
        print(f"✅ Quality metrics: {result.get('execution_metrics', {})}")

        print("\n📄 SAMPLE REPORT (first 500 chars):")
        print("-" * 40)
        print(result["final_report"][:500] + "...")

        # Show subagent results if available
        subagent_results = result.get("subagent_results", [])
        if subagent_results:
            print(f"\n🤖 SUBAGENT RESULTS ({len(subagent_results)}):")
            print("-" * 40)
            for i, subresult in enumerate(subagent_results[:3]):  # Show first 3
                print(f"[{i+1}] Agent {subresult.get('agent_id', 'N/A')}: {subresult.get('task', 'N/A')[:50]}...")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🚀 AdvancedResearch System Test Suite")
    print("=" * 50)

    # Test 1: Pydantic models
    test_pydantic_models()

    # Test 2: Check environment variables
    print("🔧 Checking environment setup...")
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: Neither OPENAI_API_KEY nor ANTHROPIC_API_KEY set. Research may fail.")
    else:
        if os.getenv("OPENAI_API_KEY"):
            print("✅ OPENAI_API_KEY found")
        if os.getenv("ANTHROPIC_API_KEY"):
            print("✅ ANTHROPIC_API_KEY found")

    if not os.getenv("EXA_API_KEY"):
        print("⚠️  Warning: EXA_API_KEY not set. Web search may use mock results.")
    else:
        print("✅ EXA_API_KEY found")

    print()

    # Test 3: Simple research
    if os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
        success = test_simple_research()
        if success:
            print("\n🎉 All tests passed! The AdvancedResearch system is working correctly.")
        else:
            print("\n❌ Research test failed. Check the logs for more details.")
    else:
        print("⏭️  Skipping research test due to missing API keys.")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY (and optionally EXA_API_KEY) to run full tests.")


if __name__ == "__main__":
    main()
