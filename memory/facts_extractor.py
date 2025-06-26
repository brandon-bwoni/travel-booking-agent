from typing import List, Dict
from datetime import datetime
from langchain_core.messages import BaseMessage

class TravelFactsExtractor:
    """Extract travel-related facts from conversations."""
    
    @staticmethod
    def extract_travel_facts(messages: List[BaseMessage], session_id: str) -> List[Dict]:
        """Extract travel-related facts from conversation with better parsing."""
        facts = []
        current_time = datetime.utcnow()
        
        for message in messages:
            if not hasattr(message, 'content'):
                continue
                
            content = message.content.lower()
            original_content = message.content
            
            # Extract booking information
            if "booking" in content and any(word in content for word in ["id", "number", "confirmation"]):
                facts.append({
                    "session_id": session_id,
                    "fact_type": "booking",
                    "content": original_content,
                    "timestamp": current_time
                })
            
            # Extract destination preferences with key-value pairs
            if any(word in content for word in ["prefer", "like", "want", "need"]):
                facts.extend(TravelFactsExtractor._extract_preferences(
                    content, original_content, session_id, current_time
                ))
            
            # Extract destination mentions
            if any(word in content for word in ["hotel", "flight", "city", "country"]):
                facts.append({
                    "session_id": session_id,
                    "fact_type": "destination",
                    "content": original_content,
                    "timestamp": current_time
                })
        
        return facts
    
    @staticmethod 
    def _extract_preferences(content: str, original_content: str, session_id: str, timestamp: datetime) -> List[Dict]:
        """Extract specific preference types."""
        facts = []
        
        if "budget" in content:
            facts.append({
                "session_id": session_id,
                "fact_type": "preference",
                "key": "budget_preference",
                "value": original_content,
                "content": original_content,
                "timestamp": timestamp
            })
        elif "location" in content or "destination" in content:
            facts.append({
                "session_id": session_id,
                "fact_type": "preference", 
                "key": "location_preference",
                "value": original_content,
                "content": original_content,
                "timestamp": timestamp
            })
        else:
            facts.append({
                "session_id": session_id,
                "fact_type": "preference",
                "key": "general_preference", 
                "value": original_content,
                "content": original_content,
                "timestamp": timestamp
            })
            
        return facts