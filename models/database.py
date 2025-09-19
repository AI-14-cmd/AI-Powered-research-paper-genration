from pymongo import MongoClient
from datetime import datetime
import os

class Database:
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def init_app(self, app):
        try:
            mongodb_uri = app.config.get('MONGODB_URI', 'mongodb://localhost:27017/research_papers')
            self._client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            self._db = self._client.get_database()
            # Test connection
            self._client.admin.command('ping')
            print("[SUCCESS] MongoDB connected successfully")
        except Exception as e:
            print(f"[ERROR] MongoDB connection failed: {e}")
            self._db = None
    
    @property
    def db(self):
        return self._db
    
    def save_paper(self, paper_data):
        if self._db is None:
            return None
        try:
            paper_data['created_at'] = datetime.utcnow()
            result = self._db.papers.insert_one(paper_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving paper: {e}")
            return None
    
    def get_paper(self, paper_id):
        if self._db is None:
            return None
        try:
            from bson import ObjectId
            return self._db.papers.find_one({'_id': ObjectId(paper_id)})
        except Exception as e:
            print(f"Error retrieving paper: {e}")
            return None

db = Database()

def init_db(app):
    db.init_app(app)