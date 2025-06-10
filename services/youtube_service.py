import os
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import isodate
import requests
from datetime import timedelta

class YouTubeService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    def search_videos(self, query, max_results=10):
        """Search YouTube videos"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': query,
            'maxResults': max_results,
            'type': 'video',
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        videos = []
        for item in data.get('items', []):
            video_id = item['id']['videoId']
            videos.append({
                'id': video_id,
                'title': item['snippet']['title'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'channel': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt']
            })
        
        # Get durations for all videos in one batch
        video_ids = [v['id'] for v in videos]
        durations = self._get_video_durations(video_ids)
        
        for video in videos:
            video['duration'] = durations.get(video['id'], 'N/A')
        
        return videos
    
    def _get_video_durations(self, video_ids):
        """Get durations for multiple videos"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'contentDetails',
            'id': ','.join(video_ids),
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        durations = {}
        for item in data.get('items', []):
            video_id = item['id']
            duration = isodate.parse_duration(item['contentDetails']['duration'])
            # Format duration as HH:MM:SS
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            durations[video_id] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return durations
    
    def get_video_info(self, video_id):
        """Get detailed info for a single video"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'snippet,contentDetails',
            'id': video_id,
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('items'):
            raise ValueError("Video not found")
        
        item = data['items'][0]
        duration = isodate.parse_duration(item['contentDetails']['duration'])
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            'id': video_id,
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'channel': item['snippet']['channelTitle'],
            'duration': f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            'published_at': item['snippet']['publishedAt']
        }
    
    def get_transcript(self, video_id):
        """Get transcript for a video"""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception as e:
            raise Exception(f"Could not retrieve transcript: {str(e)}")
    
    def extract_video_id(self, url):
        """Extract video ID from various YouTube URL formats"""
        # Handle various YouTube URL formats
        if 'youtu.be' in url:
            return url.split('/')[-1].split('?')[0]
        elif 'youtube.com' in url:
            query = urlparse(url).query
            params = parse_qs(query)
            return params.get('v', [None])[0]
        else:
            # Assume it's already a video ID
            return url
