import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from config import Config

def setup_logger():
    """Configure application logging"""
    logger = logging.getLogger('youtube_quiz_app')
    logger.setLevel(logging.DEBUG if Config.DEBUG else logging.INFO)
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        f"logs/app_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=1024 * 1024 * 5,  # 5MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
