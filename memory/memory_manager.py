from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from langchain_core.messages import BaseMessage

from .database.config import DatabaseConfig
from .message_utils import MessageSerializer
from .facts_extractor import TravelFactsExtractor
from .summarizer import ConversationSummarizer
from .embeddings_handler import EmbeddingsHandler

class TravelAgentMemory:
    """Main memory manager for travel agent conversations."""
    
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017", db_name: str = "travel_agent"):
        # Initialize components
        self.db_config = DatabaseConfig(mongo_uri, db_name)
        self.message_serializer = MessageSerializer()
        self.facts_extractor = TravelFactsExtractor()
        self.summarizer = ConversationSummarizer()
        self.embeddings_handler = EmbeddingsHandler()
        
        # Create indexes
        self.db_config.create_indexes()
        
        # Get database collections
        self.db = self.db_config.db
        self.conversations = self.db.conversations
        self.facts = self.db.facts
        self.embeddings_collection = self.db.embeddings
        self.summaries = self.db.summaries
    
    def remember(self, session_id: str, messages: List[BaseMessage], user_data: Optional[Dict] = None):
        """Store conversation interaction with facts extraction and embeddings."""
        
        # 1. Store in conversation buffer
        interaction = {
            "session_id": session_id,
            "timestamp": datetime.utcnow(),
            "messages": [self.message_serializer.serialize_message(msg) for msg in messages],
            "user_data": user_data or {}
        }
        
        conversation_id = self.conversations.insert_one(interaction).inserted_id
        
        # 2. Extract and store important travel facts
        facts = self.facts_extractor.extract_travel_facts(messages, session_id)
        if facts:
            self.facts.insert_many(facts)
        
        # 3. Create embeddings for semantic search
        content = self.message_serializer.get_conversation_content(messages)
        if content:
            self.embeddings_handler.store_embedding(
                self.db, session_id, str(conversation_id), content
            )
    
    def recall(self, session_id: str, query: str, max_conversations: int = 5) -> Dict[str, Any]:
        """Combine different memory types to recall relevant information."""
        
        # 1. Get recent conversations
        recent_conversations = list(
            self.conversations
            .find({"session_id": session_id})
            .sort("timestamp", -1)
            .limit(max_conversations)
        )
        
        # 2. Semantic search through embeddings
        relevant_conversations = self.embeddings_handler.similarity_search(
            self.db, query, session_id, k=3
        )
        
        # 3. Query relevant facts
        travel_facts = list(
            self.facts.find({
                "session_id": session_id,
                "$or": [
                    {"content": {"$regex": query, "$options": "i"}},
                    {"fact_type": {"$in": ["booking", "preference", "destination"]}}
                ]
            }).limit(10)
        )
        
        return {
            "recent_conversations": recent_conversations,
            "relevant_conversations": relevant_conversations,
            "travel_facts": travel_facts,
            "session_id": session_id
        }
    
    def store_conversation_summary(self, session_id: str, messages: List[BaseMessage], 
                                 summary_threshold: int = 10) -> None:
        """Store a summary of the conversation when it gets too long."""
        
        recent_conversations = list(
            self.conversations
            .find({"session_id": session_id})
            .sort("timestamp", -1)
            .limit(summary_threshold)
        )
        
        if len(recent_conversations) >= summary_threshold:
            older_conversations = list(
                self.conversations
                .find({"session_id": session_id})
                .sort("timestamp", 1)
                .limit(summary_threshold - 2)
            )
            
            if older_conversations:
                summary_text = self.summarizer.create_conversation_summary(older_conversations)
                
                summary_doc = {
                    "session_id": session_id,
                    "summary": summary_text,
                    "timestamp": datetime.utcnow(),
                    "conversation_count": len(older_conversations),
                    "date_range": {
                        "start": older_conversations[0]["timestamp"],
                        "end": older_conversations[-1]["timestamp"]
                    }
                }
                
                self.summaries.insert_one(summary_doc)
                
                conversation_ids = [conv["_id"] for conv in older_conversations]
                self.conversations.delete_many({"_id": {"$in": conversation_ids}})
    
    def get_conversation_summary(self, session_id: str) -> str:
        """Get the conversation summary for a session."""
        summaries = list(
            self.summaries
            .find({"session_id": session_id})
            .sort("timestamp", -1)
        )
        
        if not summaries:
            return ""
        
        combined_summary = "\n\n".join([
            f"Summary from {summary['date_range']['start'].strftime('%Y-%m-%d')} to {summary['date_range']['end'].strftime('%Y-%m-%d')}:\n{summary['summary']}"
            for summary in reversed(summaries)
        ])
        
        return combined_summary
    
    def recall_with_summary(self, session_id: str, query: str, max_conversations: int = 3) -> Dict[str, Any]:
        """Enhanced recall that includes conversation summary."""
        recall_data = self.recall(session_id, query, max_conversations)
        conversation_summary = self.get_conversation_summary(session_id)
        recall_data["conversation_summary"] = conversation_summary
        return recall_data
    
    def get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get user travel preferences from stored facts."""
        preferences = {}
        
        pref_facts = self.facts.find({
            "session_id": session_id,
            "fact_type": "preference"
        })
        
        for fact in pref_facts:
            if "key" in fact and "value" in fact:
                preferences[fact["key"]] = fact["value"]
                
        return preferences
    
    def get_booking_history(self, session_id: str) -> List[Dict]:
        """Get user's booking history."""
        return list(
            self.facts.find({
                "session_id": session_id,
                "fact_type": "booking"
            }).sort("timestamp", -1)
        )
    
    def get_chat_history(self, session_id: str, limit: int = 10) -> List[BaseMessage]:
        """Get chat history as LangChain messages."""
        conversations = list(
            self.conversations
            .find({"session_id": session_id})
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        messages = []
        for conv in reversed(conversations):
            for msg_data in conv.get("messages", []):
                message = self.message_serializer.deserialize_message(msg_data)
                if message:
                    messages.append(message)
        
        return messages[-20:]
    
    def cleanup_old_data(self, days_old: int = 30):
        """Clean up old conversation data."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        self.conversations.delete_many({"timestamp": {"$lt": cutoff_date}})
        self.embeddings_collection.delete_many({"timestamp": {"$lt": cutoff_date}})
        self.facts.delete_many({"timestamp": {"$lt": cutoff_date}})
        self.summaries.delete_many({"timestamp": {"$lt": cutoff_date}})
    
    def close(self):
        """Close database connection."""
        self.db_config.close_connection()