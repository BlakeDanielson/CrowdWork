import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional, Any
import re

class YouTubeAPI:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the YouTube API client.
        
        Args:
            api_key: YouTube Data API key. If None, will try to get from environment variable.
        """
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YouTube API key is required. Provide it as parameter or set YOUTUBE_API_KEY environment variable.")
        
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
    
    def extract_channel_id(self, channel_url: str) -> str:
        """
        Extract channel ID from various YouTube channel URL formats.
        
        Args:
            channel_url: URL or handle to a YouTube channel
            
        Returns:
            Channel ID
        """
        # Handle different YouTube URL formats
        channel_id_match = re.search(r"channel/([^/?&]+)", channel_url)
        if channel_id_match:
            return channel_id_match.group(1)
        
        # Handle user URLs
        user_match = re.search(r"user/([^/?&]+)", channel_url)
        if user_match:
            username = user_match.group(1)
            return self._get_channel_id_from_username(username)
        
        # Handle @handles
        handle_match = re.search(r"@([^/?&]+)", channel_url)
        if handle_match:
            handle = handle_match.group(1)
            return self._get_channel_id_from_handle(handle)
        
        # If it's just the channel ID itself
        if re.match(r"^UC[a-zA-Z0-9_-]{22}$", channel_url):
            return channel_url
        
        # If it's a custom URL (c/channelname)
        custom_match = re.search(r"c/([^/?&]+)", channel_url)
        if custom_match:
            custom_name = custom_match.group(1)
            return self._get_channel_id_from_custom_url(custom_name)
        
        raise ValueError(f"Could not extract channel ID from URL: {channel_url}")
    
    def _get_channel_id_from_username(self, username: str) -> str:
        """Get channel ID from a YouTube username."""
        request = self.youtube.channels().list(
            part="id",
            forUsername=username
        )
        response = request.execute()
        
        if not response.get("items"):
            raise ValueError(f"No channel found for username: {username}")
        
        return response["items"][0]["id"]
    
    def _get_channel_id_from_handle(self, handle: str) -> str:
        """Get channel ID from a YouTube handle."""
        # YouTube API doesn't directly support handle search, so we need to search for the channel
        request = self.youtube.search().list(
            part="snippet",
            q=f"@{handle}",
            type="channel",
            maxResults=1
        )
        response = request.execute()
        
        if not response.get("items"):
            raise ValueError(f"No channel found for handle: @{handle}")
        
        return response["items"][0]["snippet"]["channelId"]
    
    def _get_channel_id_from_custom_url(self, custom_url: str) -> str:
        """Get channel ID from a YouTube custom URL."""
        # Similar to handle, we need to search
        request = self.youtube.search().list(
            part="snippet",
            q=custom_url,
            type="channel",
            maxResults=1
        )
        response = request.execute()
        
        if not response.get("items"):
            raise ValueError(f"No channel found for custom URL: {custom_url}")
        
        return response["items"][0]["snippet"]["channelId"]
    
    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Get videos from a YouTube channel.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to retrieve
            
        Returns:
            List of video metadata dictionaries
        """
        # First, get the channel's upload playlist ID
        request = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()
        
        if not response.get("items"):
            raise ValueError(f"No channel found with ID: {channel_id}")
        
        # The uploads playlist contains all videos uploaded to the channel
        uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Now get the videos from the uploads playlist
        videos = []
        next_page_token = None
        
        while len(videos) < max_results:
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response["items"]:
                video_id = item["contentDetails"]["videoId"]
                title = item["snippet"]["title"]
                description = item["snippet"]["description"]
                published_at = item["snippet"]["publishedAt"]
                
                videos.append({
                    "video_id": video_id,
                    "title": title,
                    "description": description,
                    "published_at": published_at
                })
            
            next_page_token = response.get("nextPageToken")
            if not next_page_token or len(videos) >= max_results:
                break
        
        return videos
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed metadata for a list of videos.
        
        Args:
            video_ids: List of YouTube video IDs
            
        Returns:
            List of video detail dictionaries
        """
        videos = []
        # YouTube API only allows 50 videos per request
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(batch)
            )
            response = request.execute()
            
            for item in response.get("items", []):
                video_id = item["id"]
                title = item["snippet"]["title"]
                description = item["snippet"]["description"]
                duration = item["contentDetails"]["duration"]  # ISO 8601 format
                published_at = item["snippet"]["publishedAt"]
                view_count = item["statistics"].get("viewCount", 0)
                
                videos.append({
                    "video_id": video_id,
                    "title": title,
                    "description": description,
                    "duration": duration,
                    "published_at": published_at,
                    "view_count": view_count
                })
        
        return videos
    
    def get_video_transcript(self, video_id: str, language: str = "en") -> Optional[List[Dict[str, Any]]]:
        """
        Get transcript for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            language: Language code (default: "en" for English)
            
        Returns:
            List of transcript segments or None if no transcript is available
        """
        try:
            # First, get the available caption tracks for the video
            request = self.youtube.captions().list(
                part="snippet",
                videoId=video_id
            )
            response = request.execute()
            
            # Find the caption track in the requested language
            caption_id = None
            for item in response.get("items", []):
                if item["snippet"]["language"] == language:
                    caption_id = item["id"]
                    break
            
            if not caption_id:
                return None
            
            # Get the actual transcript (this is simplified - actual implementation more complex)
            # Note: The captions.download method requires OAuth2 authentication,
            # which is more complex than API key auth. For simplicity in the MVP,
            # we could use a third-party library like youtube_transcript_api instead.
            # This is just a placeholder for the structure.
            return [{"text": "Transcript text here", "start": 0.0, "duration": 1.0}]
            
        except HttpError:
            return None

    def filter_standup_videos(self, videos: List[Dict[str, Any]], min_duration_seconds: int = 120) -> List[Dict[str, Any]]:
        """
        Filter videos to only include likely stand-up comedy performances.
        
        Args:
            videos: List of video metadata dictionaries
            min_duration_seconds: Minimum video duration in seconds
            
        Returns:
            Filtered list of video dictionaries
        """
        # Keywords that might indicate stand-up comedy
        standup_keywords = [
            "stand up", "standup", "comedy", "comedian", "special",
            "live", "performance", "club", "theater", "theatre",
            "stage", "routine", "set", "jokes", "laugh"
        ]
        
        # ISO 8601 duration to seconds (simplified)
        def parse_duration(duration: str) -> int:
            match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
            if not match:
                return 0
            
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            
            return hours * 3600 + minutes * 60 + seconds
        
        filtered_videos = []
        for video in videos:
            # Check duration
            duration_seconds = parse_duration(video.get("duration", "PT0S"))
            if duration_seconds < min_duration_seconds:
                continue
            
            # Check title and description for keywords
            title = video.get("title", "").lower()
            description = video.get("description", "").lower()
            
            # Check if any keyword is in title or description
            if any(keyword in title or keyword in description for keyword in standup_keywords):
                filtered_videos.append(video)
        
        return filtered_videos 