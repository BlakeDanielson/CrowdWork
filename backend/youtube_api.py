import os
import re
import logging
import googleapiclient.discovery
from typing import List, Dict, Any, Optional, Union
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTubeAPI:
    """
    Class to interact with YouTube API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the YouTube API client.
        
        Args:
            api_key: YouTube API key (optional, can be read from environment variable)
        """
        # Get API key from environment if not provided
        self.api_key = api_key or os.environ.get('YOUTUBE_API_KEY')
        self.youtube = None
        
        if self.api_key:
            self._init_youtube_client()
        else:
            logger.warning("No YouTube API key provided. Some functionality will be limited.")
    
    def _init_youtube_client(self):
        """Initialize the YouTube API client."""
        try:
            api_service_name = "youtube"
            api_version = "v3"
            self.youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey=self.api_key)
            logger.info("YouTube API client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing YouTube API client: {e}")
            self.youtube = None
    
    def extract_channel_id(self, channel_url: str) -> str:
        """
        Extract channel ID from a YouTube channel URL.
        
        Args:
            channel_url: URL of a YouTube channel
            
        Returns:
            Channel ID
        """
        # Different URL formats for YouTube channels
        channel_id_pattern = r'youtube\.com/channel/(UC[a-zA-Z0-9_-]{22})'
        custom_url_pattern = r'youtube\.com/c/([a-zA-Z0-9_-]+)'
        user_pattern = r'youtube\.com/user/([a-zA-Z0-9_-]+)'
        handle_pattern = r'youtube\.com/@([a-zA-Z0-9_-]+)'
        
        # Try to extract channel ID directly
        match = re.search(channel_id_pattern, channel_url)
        if match:
            return match.group(1)
        
        # For custom URLs, usernames, or handles, we need to make an API call
        # but this requires an API key
        if not self.youtube:
            raise ValueError("YouTube API key required to resolve channel from custom URL, username, or handle")
        
        try:
            # Check for custom URL
            match = re.search(custom_url_pattern, channel_url)
            if match:
                custom_name = match.group(1)
                return self._get_channel_id_from_custom_url(custom_name)
            
            # Check for username
            match = re.search(user_pattern, channel_url)
            if match:
                username = match.group(1)
                return self._get_channel_id_from_username(username)
            
            # Check for handle
            match = re.search(handle_pattern, channel_url)
            if match:
                handle = match.group(1)
                return self._get_channel_id_from_handle(handle)
            
            # If we get here, the URL format is not recognized
            raise ValueError(f"Unrecognized YouTube channel URL format: {channel_url}")
            
        except Exception as e:
            logger.error(f"Error extracting channel ID: {e}")
            raise
    
    def _get_channel_id_from_custom_url(self, custom_name: str) -> str:
        """Get channel ID from custom URL."""
        request = self.youtube.search().list(
            part="snippet",
            q=custom_name,
            type="channel",
            maxResults=1
        )
        response = request.execute()
        
        if not response.get('items'):
            raise ValueError(f"No channel found with custom URL: {custom_name}")
        
        return response['items'][0]['snippet']['channelId']
    
    def _get_channel_id_from_username(self, username: str) -> str:
        """Get channel ID from username."""
        request = self.youtube.channels().list(
            part="id",
            forUsername=username
        )
        response = request.execute()
        
        if not response.get('items'):
            raise ValueError(f"No channel found with username: {username}")
        
        return response['items'][0]['id']
    
    def _get_channel_id_from_handle(self, handle: str) -> str:
        """Get channel ID from handle (similar approach as custom URL)."""
        request = self.youtube.search().list(
            part="snippet",
            q=f"@{handle}",
            type="channel",
            maxResults=1
        )
        response = request.execute()
        
        if not response.get('items'):
            raise ValueError(f"No channel found with handle: @{handle}")
        
        return response['items'][0]['snippet']['channelId']
    
    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        Get basic information about a YouTube channel.
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Dictionary with channel information
        """
        if not self.youtube:
            logger.warning("YouTube API client not initialized. Returning minimal info.")
            return {"id": channel_id, "title": "Unknown Channel"}
        
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError(f"No channel found with ID: {channel_id}")
            
            channel_info = response['items'][0]
            snippet = channel_info.get('snippet', {})
            statistics = channel_info.get('statistics', {})
            
            return {
                "id": channel_id,
                "title": snippet.get('title', 'Unknown Channel'),
                "description": snippet.get('description', ''),
                "custom_url": snippet.get('customUrl', ''),
                "published_at": snippet.get('publishedAt', ''),
                "thumbnail_url": snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                "subscriber_count": statistics.get('subscriberCount', 0),
                "video_count": statistics.get('videoCount', 0),
                "view_count": statistics.get('viewCount', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return {"id": channel_id, "title": "Unknown Channel", "error": str(e)}
    
    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Get videos from a YouTube channel.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of results to return
            
        Returns:
            List of video information dictionaries
        """
        if not self.youtube:
            raise ValueError("YouTube API client not initialized. API key required.")
        
        try:
            # First, get the upload playlist ID for the channel
            request = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            )
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError(f"No channel found with ID: {channel_id}")
            
            uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Then, get videos from the uploads playlist
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                # Limit how many results to request per page
                results_per_page = min(50, max_results - len(videos))
                
                request = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=results_per_page,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                # Extract video information
                for item in response['items']:
                    video_id = item['contentDetails']['videoId']
                    snippet = item['snippet']
                    
                    video_info = {
                        "video_id": video_id,
                        "title": snippet.get('title', 'Unknown Title'),
                        "description": snippet.get('description', ''),
                        "published_at": snippet.get('publishedAt', ''),
                        "thumbnail_url": snippet.get('thumbnails', {}).get('default', {}).get('url', '')
                    }
                    
                    videos.append(video_info)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token or len(videos) >= max_results:
                    break
            
            # Get more details for these videos (duration, view count, etc.)
            if videos:
                videos = self._enrich_video_details(videos[:max_results])
            
            return videos
            
        except Exception as e:
            logger.error(f"Error getting channel videos: {e}")
            raise
    
    def _enrich_video_details(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add additional details to video information.
        
        Args:
            videos: List of video information dictionaries
            
        Returns:
            List of enriched video information dictionaries
        """
        if not videos:
            return []
        
        try:
            # Get video IDs
            video_ids = [video['video_id'] for video in videos]
            
            # Split into chunks of 50 (API limit)
            chunks = [video_ids[i:i+50] for i in range(0, len(video_ids), 50)]
            
            # Get details for each chunk
            all_details = {}
            
            for chunk in chunks:
                request = self.youtube.videos().list(
                    part="contentDetails,statistics,status",
                    id=','.join(chunk)
                )
                response = request.execute()
                
                for item in response['items']:
                    video_id = item['id']
                    content_details = item.get('contentDetails', {})
                    statistics = item.get('statistics', {})
                    status = item.get('status', {})
                    
                    # Parse duration (PT1H2M3S format)
                    duration_str = content_details.get('duration', 'PT0S')
                    duration_seconds = self._parse_duration(duration_str)
                    
                    all_details[video_id] = {
                        "duration": duration_seconds,
                        "duration_str": duration_str,
                        "view_count": int(statistics.get('viewCount', 0)),
                        "like_count": int(statistics.get('likeCount', 0)),
                        "comment_count": int(statistics.get('commentCount', 0)),
                        "privacy_status": status.get('privacyStatus', 'unknown')
                    }
            
            # Merge details into original video list
            for video in videos:
                video_id = video['video_id']
                if video_id in all_details:
                    video.update(all_details[video_id])
            
            return videos
            
        except Exception as e:
            logger.error(f"Error enriching video details: {e}")
            return videos  # Return original list if enrichment fails
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Parse ISO 8601 duration format (PT1H2M3S) to seconds.
        
        Args:
            duration_str: ISO 8601 duration string
            
        Returns:
            Duration in seconds
        """
        hours = re.search(r'(\d+)H', duration_str)
        minutes = re.search(r'(\d+)M', duration_str)
        seconds = re.search(r'(\d+)S', duration_str)
        
        hours = int(hours.group(1)) if hours else 0
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0
        
        return hours * 3600 + minutes * 60 + seconds
    
    def filter_standup_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter videos to only include those likely to be stand-up comedy.
        
        Args:
            videos: List of video information dictionaries
            
        Returns:
            Filtered list of videos
        """
        # This is a very basic filter - in a real application you'd use more sophisticated
        # heuristics based on title, description, length, etc.
        standup_keywords = [
            'stand-up', 'standup', 'comedy', 'comedian', 'live', 'performance', 
            'special', 'routine', 'set', 'funny', 'jokes', 'comic'
        ]
        
        filtered_videos = []
        
        for video in videos:
            title = video.get('title', '').lower()
            description = video.get('description', '').lower()
            
            # Check if any keyword is in title or description
            if any(keyword in title or keyword in description for keyword in standup_keywords):
                # Check if video is long enough (usually > 5 minutes)
                if video.get('duration', 0) > 5 * 60:
                    filtered_videos.append(video)
        
        return filtered_videos
    
    def get_video_transcript(self, video_id: str, language_codes: List[str] = ['en']) -> List[Dict[str, Any]]:
        """
        Get transcript for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            language_codes: List of language codes to try, in order of preference
            
        Returns:
            List of transcript segments with text, start time, and duration
        """
        try:
            # First try to get manual transcripts in the specified languages
            try:
                return YouTubeTranscriptApi.get_transcript(video_id, languages=language_codes)
            except NoTranscriptFound:
                # If no manually created transcript is found, try generated ones
                logger.info(f"No manual transcript found for {video_id}, trying generated transcripts")
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Try to get a transcript in one of the specified languages
                for language_code in language_codes:
                    try:
                        generated_transcript = transcript_list.find_generated_transcript([language_code])
                        return generated_transcript.fetch()
                    except:
                        continue
                
                # If we didn't find a transcript in the specified languages, try any available language
                try:
                    available_transcript = next(transcript_list._manually_created_transcripts.values().__iter__())
                    return available_transcript.fetch()
                except:
                    try:
                        available_transcript = next(transcript_list._generated_transcripts.values().__iter__())
                        return available_transcript.fetch()
                    except:
                        pass
                
                # If we get here, we couldn't find any transcript
                raise NoTranscriptFound(video_id, language_codes)
                
        except TranscriptsDisabled:
            logger.warning(f"Transcripts are disabled for video {video_id}")
            return []
        except NoTranscriptFound:
            logger.warning(f"No transcript found for video {video_id} in languages {language_codes}")
            return []
        except Exception as e:
            logger.error(f"Error getting transcript for video {video_id}: {e}")
            return [] 