from advanced_research.main import AdvancedResearch

# Example 1: Traditional research mode with direct output
print("=== Example 1: Traditional Research Mode ===")
research_system = AdvancedResearch(
    name="Medical Research Team",
    description="A team of medical researchers who specialize in finding the best treatments for diabetes.",
    max_loops=1,
    export_on=True,  # Enable JSON export
    chat_interface=False,  # Traditional mode
)

# Run research and get results
result = research_system.run(
    "What are the latest and highest quality treatments for diabetes? Give me 2 queries"
)
