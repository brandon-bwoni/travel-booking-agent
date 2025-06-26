from typing import List, Dict
from datetime import datetime
from langchain_openai import OpenAIEmbeddings

class EmbeddingsHandler:
    """Handle embeddings creation and similarity search."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    def create_embedding(self, content: str) -> List[float]:
        """Create embedding for content."""
        return self.embeddings.embed_query(content)
    
    def store_embedding(self, db, session_id: str, conversation_id: str, content: str):
        """Store embedding in database."""
        embedding_vector = self.create_embedding(content)
        
        embedding_doc = {
            "session_id": session_id,
            "conversation_id": conversation_id,
            "content": content,
            "embedding": embedding_vector,
            "timestamp": datetime.utcnow()
        }
        
        db.embeddings.insert_one(embedding_doc)
    
    def similarity_search(self, db, query: str, session_id: str, k: int = 3) -> List[Dict]:
        """Simple similarity search - in production, use MongoDB Atlas Vector Search."""
        # For now, just return recent embeddings
        # In production, implement proper vector similarity
        return list(
            db.embeddings
            .find({"session_id": session_id})
            .sort("timestamp", -1)
            .limit(k)
        )