from advanced_research.main import AdvancedResearch

research_system = AdvancedResearch(
    name="Medical Research Team",
    description="A team of medical researchers who specialize in finding the best treatments for diabetes.",
    max_loops=1,
    # output_type="all",
    # export_on=True,
    export_on=True,
)

research_system.run(
    "What are the latest and highest quality treatments for diabetes? Only provide 2 queries"
)
