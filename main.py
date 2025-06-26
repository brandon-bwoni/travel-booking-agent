from langchain_openai import ChatOpenAI
from typing import Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import ToolNode
from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod
from state.state import AgentState
from nodes.classifier import classifier_node
from prompts.system import SYSTEM_PROMPT

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



def chatbot(state: AgentState):
    """Main agent function to handle user messages and invoke the LLM."""
    messages = state["messages"]
    
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT)
        ] + messages
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState):
    """Enhanced routing based on classification and confidence."""
    messages = state.get("messages", [])
    classification = state.get("classification", "unknown")
    confidence = state.get("confidence", 0.0)
    
    if not messages:
        return END
    
    last_message = messages[-1]
    
    # Check if model wants to use tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"🔧 Using tools: {[tool.get('name', 'unknown') for tool in last_message.tool_calls]}")
        return "tool_node"
    
    # Route based on classification and confidence
    if confidence < 0.3:
        print("🤔 Low confidence in classification, asking for clarification.")
        return "clarification"
    
    
    if classification in ["booking_lookup", "booking_create", "payment_update", 
                         "search_hotels", "search_flights", "search_general", "faq_question"]:
        print(f"🔄 Routing to tool node for classification: {classification}")
        return "tool_node"
    return END


def clarification_node(state: AgentState):
    """Provide helpful clarification when confidence is low."""
    clarification_message = AIMessage(content="""
🤔 I'm not quite sure what you're looking for. Let me help you! 

How may I make your travel experience easy? I can assist you with:

🔍 **Search & Discovery:**
- Find hotels in your destination
- Search for flights
- Discover attractions and activities

📋 **Booking Management:**
- Look up your existing bookings
- Create new hotel reservations
- Update payment status

❓ **Travel Information:**
- Answer questions about hotel policies
- Provide travel tips and recommendations
- Help with general travel inquiries

Please let me know what you'd like to do, and I'll be happy to help! 🌍
    """.strip())
    
    return {"messages": [clarification_message]}




tool_node = ToolNode(tools=tools)



# Define the state graph for the agent
graph = StateGraph(AgentState)

# All nodes
graph.add_node("chatbot", chatbot)
graph.add_node("classifier", classifier_node)
graph.add_node("tool_node", tool_node)
graph.add_node("clarification", clarification_node) 

# Add edges
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", "classifier")
graph.add_edge("tool_node", "chatbot")
graph.add_edge("clarification", "chatbot")  

# Add conditional edges from classifier
graph.add_conditional_edges(
    "classifier",
    should_continue,
    {
        "tool_node": "tool_node",
        "clarification": "clarification",  # New clarification route
        END: END
    }
)

app = graph.compile(checkpointer=memory)


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