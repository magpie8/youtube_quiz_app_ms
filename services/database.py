from pymongo import MongoClient
from config import Config

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.MONGO_DB_NAME]
    
    def get_collection(self, name):
        """Get a MongoDB collection"""
        return self.db[name]
    
    def log_activity(self, user_id, action, metadata=None):
        """Log user activity"""
        log_entry = {
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        self.db.activity_logs.insert_one(log_entry)
    
    def save_quiz_result(self, user_id, quiz_data):
        """Save quiz results"""
        result = {
            'user_id': user_id,
            'quiz_id': quiz_data['quiz_id'],
            'video_id': quiz_data['video_id'],
            'questions': quiz_data['questions'],
            'timestamp': datetime.now(),
            'score': quiz_data.get('score', 0),
            'total_questions': len(quiz_data['questions'])
        }
        return self.db.quiz_results.insert_one(result)
    
    def save_feedback(self, user_id, feedback_type, text):
        """Save user feedback"""
        feedback = {
            'user_id': user_id,
            'type': feedback_type,
            'text': text,
            'timestamp': datetime.now(),
            'status': 'new'
        }
        return self.db.feedback.insert_one(feedback)
