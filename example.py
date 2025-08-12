from advanced_research.main import AdvancedResearch

# Initialize the research system with export enabled
research_system = AdvancedResearch(
    name="Medical Research Team",
    description="A team of medical researchers who specialize in finding the best treatments for diabetes.",
    max_loops=1,
    output_type="all",  # Include full conversation history
    export_on=True,  # Enable JSON export
)

# Run research and get results
result = research_system.run(
    "What are the latest and highest quality treatments for diabetes?"
)

# If export_on=False, you can print the result
# print(result)
