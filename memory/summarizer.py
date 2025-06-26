from typing import List, Dict
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

class ConversationSummarizer:
    """Handle conversation summarization using LLM."""
    
    def __init__(self):
        self.summary_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    def create_conversation_summary(self, conversations: List[Dict]) -> str:
        """Create a summary of multiple conversations using LLM."""
        
        # Extract all messages from conversations
        all_messages = []
        for conv in conversations:
            for msg_data in conv.get("messages", []):
                msg_type = msg_data.get("type", "")
                content = msg_data.get("content", "")
                all_messages.append(f"{msg_type}: {content}")
        
        conversation_text = "\n".join(all_messages)
        
        # Create summary prompt
        summary_prompt = f"""
Please create a concise summary of this travel booking conversation history. Focus on:
1. User's travel preferences and requirements
2. Bookings made or inquired about
3. Important decisions or outcomes
4. Key facts that would be useful for future conversations

Conversation History:
{conversation_text}

Summary:"""
        
        try:
            summary_response = self.summary_llm.invoke([HumanMessage(content=summary_prompt)])
            return summary_response.content
        except Exception as e:
            # Fallback to simple text summary if LLM fails
            return f"Conversation summary covering {len(conversations)} interactions about travel booking and inquiries."