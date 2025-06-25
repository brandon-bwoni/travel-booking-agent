from langchain_openai import ChatOpenAI
from typing import Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import ToolNode
from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod
from state.state import AgentState


# Import your tools
from tools.booking_tool import booking_lookup_tool, booking_create_tool, payment_update_tool
from tools.faq_tool import faq_tool
from tools.search_tools import search_tool, hotel_search_tool, flight_search_tool


# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.1
)

# Set up memory
memory = MemorySaver()

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


# System message to define the agent's role
SYSTEM_MESSAGE = """
You are a helpful travel booking assistant. You can help users with:

1. 🔍 **Search for travel information** (hotels, flights, attractions)
2. 📋 **Look up existing bookings** by booking ID
3. 🏨 **Create new hotel bookings**
4. 💳 **Update payment status** for bookings
5. ❓ **Answer FAQ questions** about hotels and travel

Always be polite, helpful, and provide clear information. When creating bookings, make sure to collect all necessary details (hotel name, location, dates, price).
"""


def chatbot(state: AgentState):
    """Main agent function to handle user messages and invoke the LLM."""
    messages = state["messages"]
    
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [
            SystemMessage(content=SYSTEM_MESSAGE)
        ] + messages
    
    response = llm_with_tools.invoke(messages)
    print(f"🤖 Assistant: {response.content}")
    return {"messages": [response]}


def should_continue(state: AgentState):
    """Check if we need to continue to tools or end."""
    messages = state.get("messages", [])
    last_message = messages[-1]
    
    # Check if model wants to use tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"
    return END




tool_node = ToolNode(tools=tools)



# Define the state graph for the agent
graph = StateGraph(AgentState)
graph.add_node("chatbot", chatbot)
graph.add_node("tool_node", tool_node)

graph.add_edge(START, "chatbot")

graph.add_conditional_edges(
    "chatbot",
    should_continue,
    {
        "tool_node": "tool_node",
        END: END
    })


graph.add_edge("tool_node", "chatbot")


app = graph.compile(checkpointer=memory)


# Graph visualization
def visualize_graph():
    """Visualize the state graph using Mermaid."""
    display(
        Image(
            app.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API
         )
        )
    )

visualize_graph()    


def run_agent():
    """Run the travel booking agent with conversation loop."""
    print("🌍 Travel Booking Assistant Online! 🌍")
    print("I can help you search for travel info, manage bookings, and answer questions.")
    print("Type 'bye', 'exit', or 'quit' to end the conversation.\n")
    
    # Configuration for the agent
    config = {
        "configurable": {
            "thread_id": "travel_session_1"
        }
    }
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['bye', 'exit', 'quit']:
                print("👋 Thanks for using Travel Booking Assistant! Have a great trip!")
                break
            
            if not user_input:
                print("Please enter a message or type 'bye' to exit.")
                continue
            
            # Create message with system context
            user_message = HumanMessage(content=user_input)
            
            # Get response from agent
            response = app.invoke(
                {"messages": [user_message]},
                config=config
            )
            
            # Extract the assistant's response
            assistant_message = response["messages"][-1].content
            print(f"🤖 Assistant: {assistant_message}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")
            print("Please try again or type 'bye' to exit.\n")

if __name__ == "__main__":
    run_agent()