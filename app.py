from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from state.state import AgentState
from memory import TravelAgentMemory, MongoDBChatMessageHistory
from prompts.system import SYSTEM_PROMPT
import uuid
from typing import Dict

# Import your tools
from tools.booking_tool import booking_lookup_tool, booking_create_tool, payment_update_tool
from tools.faq_tool import faq_tool
from tools.search_tools import search_tool, hotel_search_tool, flight_search_tool


llm = ChatOpenAI(
    model="gpt-4o"
)

# Set up memory
travel_memory = TravelAgentMemory()

# Define all tools
tools = [
    booking_lookup_tool,
    booking_create_tool, 
    payment_update_tool,
    faq_tool,
    search_tool,
    hotel_search_tool,
    flight_search_tool
]


llm_with_tools = llm.bind_tools(tools=tools)

# Global memory instances for session management
user_memories: Dict[str, TravelAgentMemory] = {}

def get_or_create_memory(session_id: str) -> TravelAgentMemory:
    """Get existing memory or create new one for session."""
    if session_id not in user_memories:
        user_memories[session_id] = travel_memory
    return user_memories[session_id]

def memory_loader(state: AgentState) -> AgentState:
    """Load memory context with summaries and user data."""
    session_id = state.get("session_id") or str(uuid.uuid4())
    
    # Skip memory loading for first message
    if len(state["messages"]) <= 1:
        return {
            **state,
            "session_id": session_id,
            "memory_context": None,
            "user_preferences": {},
            "booking_history": []
        }
    
    # Get memory instance
    memory = get_or_create_memory(session_id)
    
    # Get latest user message for context
    latest_message = state["messages"][-1]
    query = latest_message.content if hasattr(latest_message, 'content') else ""
    
    # Load comprehensive memory context
    memory_context = memory.recall_with_summary(session_id, query)
    user_preferences = memory.get_user_preferences(session_id)
    booking_history = memory.get_booking_history(session_id)
    
    return {
        **state,
        "session_id": session_id,
        "memory_context": memory_context,
        "user_preferences": user_preferences,
        "booking_history": booking_history
    }

def chatbot_with_memory(state: AgentState) -> AgentState:
    """Enhanced chatbot with comprehensive memory integration."""
    messages = state["messages"]
    session_id = state.get("session_id")
    memory_context = state.get("memory_context")
    user_preferences = state.get("user_preferences", {})
    booking_history = state.get("booking_history", [])
    
    # Get memory instance
    memory = get_or_create_memory(session_id)
    
    # Build enhanced system prompt with memory context
    enhanced_prompt = SYSTEM_PROMPT
    
    if memory_context or user_preferences or booking_history:
        memory_info = f"""

**MEMORY CONTEXT FOR PERSONALIZED ASSISTANCE:**

**Conversation Summary:**
{memory_context.get('conversation_summary', 'No previous conversation summary available.')}

**User Preferences:**
{user_preferences if user_preferences else 'No preferences stored yet.'}

**Booking History:**
- Total Bookings: {len(booking_history)}
- Recent Bookings: {booking_history[:3] if booking_history else 'No previous bookings found.'}

**Recent Conversation Context:**
- Previous Interactions: {len(memory_context.get('recent_conversations', []))} recent conversations
- Relevant Facts: {len(memory_context.get('travel_facts', []))} travel-related facts stored

**Instructions:**
Use this context to provide personalized assistance. Reference previous conversations, preferences, and booking patterns when relevant. Be conversational and acknowledge returning users appropriately.
"""
        enhanced_prompt += memory_info
    
    # Prepare messages with enhanced system prompt
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=enhanced_prompt)] + messages
    else:
        # Update existing system message with memory context
        messages = [SystemMessage(content=enhanced_prompt)] + messages[1:]
    
    # Get LLM response
    response = llm_with_tools.invoke(messages)
    
    # Store conversation in memory with summarization check
    if session_id:
        # Store the user message and AI response
        conversation_messages = [messages[-1], response]  # Last user message + AI response
        memory.remember(session_id, conversation_messages)
        
        # Check if we need to create a summary (every 10 interactions)
        memory.store_conversation_summary(session_id, conversation_messages, summary_threshold=10)
    
    return {"messages": [response]}

def should_continue(state: AgentState):
    """Check if we should continue to tools or end the conversation."""
    messages = state.get("messages", [])
    if not messages:
        return END
    
    last_message = messages[-1]
    
    # Check if model wants to use tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"🔧 Using tools: {[tool.get('name', 'unknown') for tool in last_message.tool_calls]}")
        return "tools"
    
    return END




tool_node = ToolNode(tools=tools)


# Create the graph with memory integration
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("memory_loader", memory_loader)
graph.add_node("agent", chatbot_with_memory)
graph.add_node("tools", ToolNode(tools))

# Define edges
graph.add_edge(START, "memory_loader")
graph.add_edge("memory_loader", "agent")
graph.add_edge("tools", "agent")

graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

# Compile the graph
app = graph.compile()


# Graph visualization
# def visualize_graph():
#     """Visualize the state graph using Mermaid."""
#     display(
#         Image(
#             app.get_graph().draw_mermaid_png(
#             draw_method=MermaidDrawMethod.API
#          )
#         )
#     )

# visualize_graph()    

def display_user_profile(session_id: str, memory: TravelAgentMemory):
    """Display user profile information."""
    preferences = memory.get_user_preferences(session_id)
    booking_history = memory.get_booking_history(session_id)
    summary = memory.get_conversation_summary(session_id)
    
    print("\n" + "="*50)
    print(f"📊 USER PROFILE: {session_id[:8]}...")
    print("="*50)
    
    if preferences:
        print("🎯 PREFERENCES:")
        for key, value in preferences.items():
            print(f"  • {key}: {value}")
    else:
        print("🎯 PREFERENCES: None stored yet")
    
    print(f"\n📋 BOOKING HISTORY: {len(booking_history)} total bookings")
    if booking_history:
        for i, booking in enumerate(booking_history[:3]):  # Show last 3
            print(f"  {i+1}. {booking.get('content', 'Booking details')}")
    
    if summary:
        print(f"\n📝 CONVERSATION SUMMARY:")
        print(f"  {summary[:200]}..." if len(summary) > 200 else f"  {summary}")
    else:
        print("\n📝 CONVERSATION SUMMARY: No summary available yet")
    
    print("="*50 + "\n")


def run_agent_with_memory():
    """Run the travel booking agent with persistent memory and enhanced features."""
    print("🌍 TRAVEL BOOKING ASSISTANT WITH MEMORY 🌍")
    print("=" * 60)
    print("✨ Features:")
    print("  • Remembers your preferences and conversation history")
    print("  • Provides personalized travel recommendations")
    print("  • Tracks your booking history")
    print("  • Smart conversation summaries")
    print("=" * 60)
    
    # Session management
    print("\n🔑 SESSION MANAGEMENT:")
    session_choice = input("Enter your user ID (or press Enter for new session): ").strip()
    
    if session_choice:
        session_id = session_choice
        # Check if user has previous data
        memory_context = travel_memory.recall(session_id, "previous conversations")
        if memory_context.get("recent_conversations"):
            print(f"👋 Welcome back! Found {len(memory_context['recent_conversations'])} previous conversations.")
            
            # Ask if user wants to see their profile
            show_profile = input("Would you like to see your profile? (y/n): ").lower().strip()
            if show_profile in ['y', 'yes']:
                display_user_profile(session_id, travel_memory)
        else:
            print(f"🆕 New user profile created: {session_id}")
    else:
        session_id = str(uuid.uuid4())
        print(f"🆕 New session created: {session_id[:8]}...")
    
    print(f"\n💬 Chat active for session: {session_id[:8]}...")
    print("Type 'profile' to see your profile, 'help' for commands, or 'bye' to exit.\n")
    
    config = {
        "configurable": {
            "thread_id": session_id
        }
    }
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['bye', 'exit', 'quit']:
                print("👋 Thanks for using Travel Booking Assistant!")
                print(f"💾 Your conversation has been saved under session: {session_id[:8]}...")
                
                # Offer to create final summary
                create_summary = input("Create a final summary of this session? (y/n): ").lower().strip()
                if create_summary in ['y', 'yes']:
                    travel_memory.store_conversation_summary(session_id, [], summary_threshold=1)
                    print("✅ Final summary created and saved!")
                
                break
            
            elif user_input.lower() == 'profile':
                display_user_profile(session_id, travel_memory)
                continue
            
            elif user_input.lower() == 'help':
                print("\n🔧 AVAILABLE COMMANDS:")
                print("  • 'profile' - View your user profile and preferences")
                print("  • 'help' - Show this help message")
                print("  • 'bye/exit/quit' - End conversation")
                print("  • Ask about hotels, flights, bookings, or travel questions!\n")
                continue
            
            elif user_input.lower() == 'clear':
                confirm = input("⚠️  Clear all memory for this session? (type 'yes' to confirm): ")
                if confirm.lower() == 'yes':
                    travel_memory.conversations.delete_many({"session_id": session_id})
                    travel_memory.facts.delete_many({"session_id": session_id})
                    travel_memory.summaries.delete_many({"session_id": session_id})
                    travel_memory.embeddings_collection.delete_many({"session_id": session_id})
                    print("🗑️  Memory cleared for this session!")
                continue
            
            if not user_input:
                print("Please enter a message or type 'help' for commands.")
                continue
            
            # Process normal conversation
            response = app.invoke(
                {
                    "messages": [HumanMessage(content=user_input)],
                    "session_id": session_id
                },
                config=config
            )
            
            print(f"🤖 Assistant: {response['messages'][-1].content}\n")
            
        except KeyboardInterrupt:
            print(f"\n👋 Goodbye! Session saved as: {session_id[:8]}...")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Please try again or type 'help' for commands.\n")

def cleanup_memory():
    """Utility function to cleanup old memory data."""
    print("🧹 Cleaning up old memory data...")
    travel_memory.cleanup_old_data(days_old=30)
    print("✅ Cleanup completed!")

if __name__ == "__main__":
    try:
        run_agent_with_memory()
    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
    finally:
        # Close database connection
        travel_memory.close()
        print("🔒 Database connection closed")