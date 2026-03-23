from pymongo import MongoClient
from config import settings
from typing import Optional

class MongoDBConnection:
    _instance: Optional['MongoDBConnection'] = None
    
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]
    
    @classmethod
    def get_instance(cls) -> 'MongoDBConnection':
        if cls._instance is None:
            cls._instance = MongoDBConnection()
        return cls._instance
    
    def get_db(self):
        return self.db
    
    def close(self):
        if self.client:
            self.client.close()

def get_db():
    """Dependency injection for database"""
    return MongoDBConnection.get_instance().get_db()
