from typing import Dict, Optional
from datetime import datetime
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

class MessageSerializer:
    """Utilities for serializing and deserializing LangChain messages."""
    
    @staticmethod
    def serialize_message(message: BaseMessage) -> Dict:
        """Convert LangChain message to dict for MongoDB storage."""
        return {
            "type": message.__class__.__name__,
            "content": message.content,
            "additional_kwargs": getattr(message, 'additional_kwargs', {}),
            "timestamp": datetime.utcnow()
        }
    
    @staticmethod
    def deserialize_message(msg_data: Dict) -> Optional[BaseMessage]:
        """Convert MongoDB dict back to LangChain message."""
        msg_type = msg_data.get("type")
        content = msg_data.get("content", "")
        
        if msg_type == "HumanMessage":
            return HumanMessage(content=content)
        elif msg_type == "AIMessage":
            return AIMessage(content=content)
        elif msg_type == "SystemMessage":
            return SystemMessage(content=content)
        
        return None
    
    @staticmethod
    def get_conversation_content(messages: list[BaseMessage]) -> str:
        """Extract content for embedding creation."""
        return " ".join([msg.content for msg in messages if hasattr(msg, 'content')])