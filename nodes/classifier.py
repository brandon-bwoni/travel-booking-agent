from typing import  Tuple
import re
from state.state import AgentState, TravelIntentType

def classify_travel_intent(message_content: str) -> Tuple[TravelIntentType, float]:
    """Classify travel-related intents with confidence scoring.
    
    Args:
        message_content: The user's message content
        
    Returns:
        Tuple of (classification, confidence_score)
    """
    content = message_content.lower().strip()
    
    # Define classification patterns with confidence scores
    patterns = {
        "greeting": {
            "patterns": [r"\b(hello|hi|hey|good morning|good afternoon|good evening)\b"],
            "confidence": 0.9
        },
        "inquiry": {
          "patterns": [r"\b(inquire|ask|question|need\s+help|help)\b", r"\bcan\s+you\s+tell\s+me\b", r"\bwhat\s+is\b"],
          "confidence": 0.85
          },
        "booking_lookup": {
            "patterns": [r"\b(lookup|find|check|view)\s+(booking|reservation)", r"\bbooking\s+(id|number)", r"\bmy\s+booking\b"],
            "confidence": 0.85
        },
        "booking_create": {
            "patterns": [r"\b(book|reserve|create)\s+(hotel|room)", r"\bmake\s+a\s+(booking|reservation)", r"\bI\s+want\s+to\s+book\b"],
            "confidence": 0.85
        },
        "payment_update": {
            "patterns": [r"\b(pay|payment|paid)", r"\bupdate\s+payment", r"\bmark\s+as\s+paid\b"],
            "confidence": 0.8
        },
        "search_hotels": {
            "patterns": [r"\bhotels?\s+in\b", r"\bfind\s+hotels?\b", r"\bwhere\s+to\s+stay\b"],
            "confidence": 0.8
        },
        "search_flights": {
            "patterns": [r"\bflights?\s+(from|to)\b", r"\bfind\s+flights?\b", r"\bfly\s+(from|to)\b"],
            "confidence": 0.8
        },
        "search_general": {
            "patterns": [r"\bsearch\s+for\b", r"\bfind\s+information\b", r"\btell\s+me\s+about\b"],
            "confidence": 0.7
        },
        "faq_question": {
            "patterns": [r"\bwhat\s+is\b", r"\bhow\s+do\s+I\b", r"\bcan\s+you\s+explain\b", r"\bpolicy\b", r"\brules\b"],
            "confidence": 0.75
        },
        "goodbye": {
            "patterns": [r"\b(bye|goodbye|see you|thanks|thank you)\b", r"\bthat\'s all\b"],
            "confidence": 0.9
        }
    }
    
    # Check each pattern
    for intent, data in patterns.items():
        for pattern in data["patterns"]:
            if re.search(pattern, content):
                return intent, data["confidence"]
    
    # Default to unknown with low confidence
    return "unknown", 0.1

def classifier_node(state: AgentState) -> AgentState:
    """Classify the latest message and update state with intent and confidence.
    
    Args:
        state: Current agent state with messages
        
    Returns:
        Updated state with classification and confidence
    """
    if not state["messages"]:
        return {
            **state,
            "classification": "unknown",
            "confidence": 0.0
        }
    
    # Get the latest message content
    latest_message = state["messages"][-1]
    message_content = latest_message.content if hasattr(latest_message, 'content') else str(latest_message)
    
    # Classify the intent
    classification, confidence = classify_travel_intent(message_content)
    
    # Return updated state
    return {
        **state,
        "classification": classification,
        "confidence": confidence
    }