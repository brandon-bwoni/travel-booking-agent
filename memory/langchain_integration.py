from typing import List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from .memory_manager import TravelAgentMemory

class MongoDBChatMessageHistory(BaseChatMessageHistory):
    """LangChain-compatible chat message history using MongoDB."""
    
    def __init__(self, session_id: str, memory: TravelAgentMemory):
        self.session_id = session_id
        self.memory = memory
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve messages from MongoDB."""
        return self.memory.get_chat_history(self.session_id)
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the chat history."""
        self.memory.remember(self.session_id, [message])
    
    def clear(self) -> None:
        """Clear the chat history."""
        self.memory.conversations.delete_many({"session_id": self.session_id})
        self.memory.facts.delete_many({"session_id": self.session_id})
        self.memory.embeddings_collection.delete_many({"session_id": self.session_id})
        self.memory.summaries.delete_many({"session_id": self.session_id})