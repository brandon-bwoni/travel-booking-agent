from typing import Annotated, Optional, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Literal

# Define the travel-specific classification types
TravelIntentType = Literal[
    "greeting",
    "booking_lookup", 
    "booking_create",
    "inquiry",
    "payment_update",
    "search_hotels",
    "search_flights", 
    "search_general",
    "faq_question",
    "goodbye",
    "unknown"
]

class AgentState(TypedDict):
    """Enhanced state container for travel booking agent with intent classification.

    This implementation provides:
    1. Message storage with proper LangGraph annotations
    2. Intent classification for better routing
    3. Confidence scoring for decision-making
    4. Travel-specific context tracking

    Attributes:
        messages: List of conversation messages with add_messages annotation
        classification: Current message intent classification
        confidence: Classification confidence score (0.0 to 1.0)
        current_booking_context: Context for ongoing booking operations
        user_preferences: User preferences and settings
        session_data: Additional session-specific data

    The classification system enables:
    - Intelligent routing to appropriate tools
    - Confidence-based fallback strategies
    - Context-aware conversation flow
    """
    messages: Annotated[list[BaseMessage], add_messages]
    classification: TravelIntentType
    confidence: float
    current_booking_context: Optional[dict]
    user_preferences: Optional[dict] 
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: Optional[str]
    memory_context: Optional[Dict[str, Any]]
    user_preferences: Optional[Dict[str, Any]]
    booking_history: Optional[list]