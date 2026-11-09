import json

from advanced_research.main import AdvancedResearch

research_system = AdvancedResearch(
    name="Medical Research Team",
    description="A team of medical researchers who specialize in finding the best treatments for diabetes.",
    max_loops=1,
    output_type="dict",
    director_model_name="gpt-5.5",
    worker_model_name="gpt-5.4-mini",
    verbose=True,
)

# Run research and get results
result = research_system.run(
    "What are the latest and highest quality treatments for diabetes?"
)
print(json.dumps(result, indent=4))
print(json.dumps(research_system.get_usage(), indent=4))
