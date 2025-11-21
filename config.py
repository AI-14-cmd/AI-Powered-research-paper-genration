import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/research_papers')
    SECRET_KEY = os.getenv('SECRET_KEY', 'hackathon-secret-key-2024')