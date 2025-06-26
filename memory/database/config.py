from pymongo import MongoClient
from typing import Optional

class DatabaseConfig:
    """MongoDB database configuration and connection management."""
    
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017", db_name: str = "travel_agent"):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self._client: Optional[MongoClient] = None
        self._db = None
    
    @property
    def client(self) -> MongoClient:
        """Get MongoDB client, creating connection if needed."""
        if self._client is None:
            self._client = MongoClient(self.mongo_uri)
        return self._client
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            self._db = self.client[self.db_name]
        return self._db
    
    def close_connection(self):
        """Close database connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
    
    def create_indexes(self):
        """Create database indexes for better performance."""
        db = self.db
        
        # Conversations indexes
        db.conversations.create_index([("session_id", 1), ("timestamp", -1)])
        
        # Facts indexes
        db.facts.create_index([("session_id", 1), ("fact_type", 1)])
        
        # Embeddings indexes
        db.embeddings.create_index([("session_id", 1)])
        
        # Summaries indexes
        db.summaries.create_index([("session_id", 1), ("timestamp", -1)])