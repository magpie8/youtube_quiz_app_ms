from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class AuthService:
    def __init__(self, db):
        self.db = db
    
    def register_user(self, username, email, password):
        """Register a new user"""
        # Check if username or email already exists
        if self.db.users.find_one({'username': username}):
            return {'success': False, 'message': 'Username already exists'}
        
        if self.db.users.find_one({'email': email}):
            return {'success': False, 'message': 'Email already exists'}
        
        # Create new user
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.now(),
            'last_login': None,
            'is_active': True
        }
        
        try:
            result = self.db.users.insert_one(user_data)
            
            # Log the registration
            self.db.activity_logs.insert_one({
                'user_id': result.inserted_id,
                'action': 'register',
                'timestamp': datetime.now(),
                'details': {'ip': '127.0.0.1'}  # In production, get real IP
            })
            
            return {'success': True, 'message': 'Registration successful'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def login_user(self, username, password):
        """Authenticate a user"""
        user = self.db.users.find_one({'username': username})
        if not user:
            return {'success': False, 'message': 'Invalid username or password'}
        
        if not check_password_hash(user['password_hash'], password):
            return {'success': False, 'message': 'Invalid username or password'}
        
        # Update last login
        self.db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'last_login': datetime.now()}}
        )
        
        # Log the login
        self.db.activity_logs.insert_one({
            'user_id': user['_id'],
            'action': 'login',
            'timestamp': datetime.now(),
            'details': {'ip': '127.0.0.1'}  # In production, get real IP
        })
        
        return {'success': True, 'message': 'Login successful', 'user_data': user}
    
    def log_activity(self, user_id, action, details=None):
        """Log user activity"""
        log_entry = {
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.now(),
            'details': details or {}
        }
        self.db.activity_logs.insert_one(log_entry)
