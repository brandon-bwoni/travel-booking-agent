from typing import Annotated, Optional, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

class AgentState(TypedDict):
    """Enhanced state with memory integration."""
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: Optional[str]
    memory_context: Optional[Dict[str, Any]]
    user_preferences: Optional[Dict[str, Any]]
    booking_history: Optional[list]