from advanced_research.main import AdvancedResearch

# Example 1: Traditional research mode with direct output
print("=== Example 1: Traditional Research Mode ===")
research_system = AdvancedResearch(
    name="Medical Research Team",
    description="A team of medical researchers who specialize in finding the best treatments for diabetes.",
    max_loops=1,
    output_type="all",  # Include full conversation history
    export_on=True,  # Enable JSON export
    chat_interface=False,  # Traditional mode
)

# Run research and get results
result = research_system.run(
    "What are the latest and highest quality treatments for diabetes?"
)

print("Research completed! Check the exported JSON file for results.")

# Example 2: Chat Interface Mode (uncomment to use)
print("\n=== Example 2: Chat Interface Mode ===")
print("Uncomment the code below to launch the Gradio chat interface:")
print(
    """
# Initialize the research system with chat interface enabled
chat_research_system = AdvancedResearch(
    name="Advanced Research Chat Interface",
    description="Interactive research assistant powered by advanced AI agents. Ask any research question and get comprehensive findings.",
    max_loops=1,
    output_type="all",
    export_on=False,  # Disable export in chat mode
    chat_interface=True,  # Enable chat interface
)

# Launch the chat interface (no task needed, run() can be left empty)
chat_research_system.run()  # This will launch the Gradio interface
"""
)

# Uncomment below to actually launch the chat interface:
"""
chat_research_system = AdvancedResearch(
    name="Advanced Research Chat Interface", 
    description="Interactive research assistant powered by advanced AI agents. Ask any research question and get comprehensive findings.",
    max_loops=1,
    output_type="all",
    export_on=False,
    chat_interface=True,
)

# Launch the chat interface
chat_research_system.run()
"""
