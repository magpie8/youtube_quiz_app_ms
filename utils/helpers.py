from datetime import datetime

def format_timestamp(timestamp):
    """Format timestamp for display"""
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def validate_youtube_url(url):
    """Validate YouTube URL or video ID"""
    if not url:
        return False
    
    # Check if it's a video ID (simple check)
    if len(url) == 11 and all(c.isalnum() or c in ['-', '_'] for c in url):
        return True
    
    # Check common YouTube URL patterns
    patterns = [
        'youtube.com/watch?v=',
        'youtu.be/'
    ]
    
    return any(pattern in url for pattern in patterns)
