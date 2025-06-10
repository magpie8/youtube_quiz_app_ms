import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'youtube_quiz_app')
    
    # YouTube API
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    # DeepSeek API
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    
    # Flask secret key
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Debug mode
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
