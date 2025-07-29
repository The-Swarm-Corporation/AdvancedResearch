#!/usr/bin/env python3
"""
Simple test script for the enhanced MultiAgentResearchSystem with Pydantic models.
"""

import os
import sys
from pathlib import Path
from advanced_research.main import MultiAgentResearchSystem, ResearchFindings, SourceInfo

def test_pydantic_models():
    """Test that Pydantic models work correctly."""
    print("🧪 Testing Pydantic models...")
    
    # Test SourceInfo model
    source = SourceInfo(
        source="https://example.com",
        content="Test content"
    )
    print(f"✅ SourceInfo model: {source.source}")
    
    # Test ResearchFindings model
    findings = ResearchFindings(
        findings="Test findings about AI in healthcare",
        sources=[source]
    )
    print(f"✅ ResearchFindings model: {len(findings.sources)} sources")
    
    print("✅ All Pydantic models working correctly!\n")

def test_simple_research():
    """Test a simple research query with reduced complexity."""
    print("🔬 Testing simplified research system...")
    
    # Create research system with minimal settings
    research_system = MultiAgentResearchSystem(
        model_name="gpt-4o",
        max_iterations=1,  # Reduced to 1 for quick test
        max_workers=2,     # Reduced workers
        adaptive_scaling=False,  # Disable adaptive scaling for predictability
        cost_optimization=True
    )
    
    # Simple test query
    test_query = "What are the main benefits of AI in healthcare?"
    
    print(f"🔍 Testing query: '{test_query}'")
    print("⏳ Running research (this may take a moment)...\n")
    
    try:
        result = research_system.run(test_query)
        
        print("=" * 60)
        print("📊 RESEARCH RESULTS:")
        print("=" * 60)
        print(f"✅ Final report generated: {len(result['final_report'])} characters")
        print(f"✅ Sources found: {len(result.get('sources', []))}")
        print(f"✅ Quality metrics: {result.get('quality_metrics', {})}")
        
        print("\n📄 SAMPLE REPORT (first 500 chars):")
        print("-" * 40)
        print(result['final_report'][:500] + "...")
        
        if result.get('sources'):
            print(f"\n🔗 SOURCES ({len(result['sources'])}):")
            print("-" * 40)
            for i, source in enumerate(result['sources'][:3]):  # Show first 3
                print(f"[{i+1}] {source.get('source', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Enhanced Research System Test Suite")
    print("=" * 50)
    
    # Test 1: Pydantic models
    test_pydantic_models()
    
    # Test 2: Check environment variables
    print("🔧 Checking environment setup...")
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Research may fail.")
    else:
        print("✅ OPENAI_API_KEY found")
        
    if not os.getenv("EXA_API_KEY"):
        print("⚠️  Warning: EXA_API_KEY not set. Web search may fail.")
    else:
        print("✅ EXA_API_KEY found")
    
    print()
    
    # Test 3: Simple research
    if os.getenv("OPENAI_API_KEY") and os.getenv("EXA_API_KEY"):
        success = test_simple_research()
        if success:
            print("\n🎉 All tests passed! The enhanced system is working correctly.")
        else:
            print("\n❌ Research test failed. Check the logs for more details.")
    else:
        print("⏭️  Skipping research test due to missing API keys.")
        print("   Set OPENAI_API_KEY and EXA_API_KEY to run full tests.")

if __name__ == "__main__":
    main() 