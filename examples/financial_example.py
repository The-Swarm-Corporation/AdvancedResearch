from advanced_research.main import AdvancedResearch

research_system = AdvancedResearch(
    name="Financial Research Team",
    description=(
        "A team of financial researchers who specialize in finding the best "
        "treatments for financials."
    ),
    max_loops=1,
    export_on=False,  # Enable JSON export
    chat_interface=False,  # Traditional mode
)

query = (
    "What are the top 10 best energy companies that are investing in AI to invest in? "
    "Create a comprehensive analysis on each one. Give me 2 queries."
)

result = research_system.run(query)

print(result)
