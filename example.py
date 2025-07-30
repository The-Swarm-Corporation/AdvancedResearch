from advanced_research import AdvancedResearch

# Initialize the system with all configuration parameters
research_system = AdvancedResearch(
    max_iterations=1, max_search_results=2, max_subagent_iterations=1, max_workers=2
)

# Run research
results = research_system.run("What are the latest developments in quantum computing?")

print(results)
