from advanced_research import AdvancedResearch

# Set up the research system with desired configuration
research_system = AdvancedResearch(
    max_iterations=1, max_search_results=2, max_subagent_iterations=1, max_workers=2
)

# Generate a report on the best treatments for diabetes
report = research_system.research(
    "Create a comprehensive report on the best treatments for diabetes"
)

print(report)
