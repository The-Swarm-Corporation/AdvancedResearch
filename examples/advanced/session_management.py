#!/usr/bin/env python3
"""
Session Management Example for Advanced Research

This example shows how to use session management features
including conversation history and session persistence.
"""

from advanced_research import AdvancedResearch


def session_example():
    """Demonstrate session management capabilities."""

    # Initialize with session tracking
    research_system = AdvancedResearch(
        name="Session Research Team",
        description="Research system with session management",
        max_loops=1,
        export_on=False,
    )

    # First conversation
    conversation1 = research_system.run(
        "What are the basics of machine learning?"
    )

    # Second conversation (builds on first)
    conversation2 = research_system.run(
        "Can you elaborate on supervised learning specifically?"
    )

    # Third conversation (continues the session)
    conversation3 = research_system.run(
        "What about unsupervised learning methods?"
    )

    # Get conversation history
    history = research_system.conversation.history

    # Get session ID
    session_id = research_system.session_id

    return {
        "conversation1": conversation1,
        "conversation2": conversation2,
        "conversation3": conversation3,
        "history": history,
        "session_id": session_id,
    }


def conversation_continuation():
    """Show how conversations can be continued across multiple queries."""

    # Initialize system
    research_system = AdvancedResearch(
        name="Conversation Research Team",
        description="Research system for continuous conversations",
        max_loops=1,
        output_type="all",
    )

    # Start a conversation thread
    initial_query = (
        "What are the main branches of artificial intelligence?"
    )
    initial_result = research_system.run(initial_query)

    # Continue the conversation
    follow_up = "Which of these branches is most promising for near-term applications?"
    follow_up_result = research_system.run(follow_up)

    # Another follow-up
    final_query = "What are the key challenges in that area?"
    final_result = research_system.run(final_query)

    return {
        "initial": initial_result,
        "follow_up": follow_up_result,
        "final": final_result,
    }


if __name__ == "__main__":
    session_example()
    conversation_continuation()
