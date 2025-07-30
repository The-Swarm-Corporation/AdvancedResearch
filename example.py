from advanced_research import AdvancedResearch

# Initialize the system
research_system = AdvancedResearch(max_iterations=1)

# Run research
results = research_system.research(
    "What are the latest developments in quantum computing?",
    export=True,
    export_path="quantum_computing_report.md",
)

print(results)
