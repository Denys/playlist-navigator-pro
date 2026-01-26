#!/usr/bin/env python3
"""
YouTube Data API v3 integration for playlist indexing.
Extracts playlist video data with enhanced metadata.
"""

import re
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs


class YouTubeAPIExtractor:
    """Extract playlist data using YouTube Data API v3."""
    
    def __init__(self, api_key: str):
        """
        Initialize YouTube API client.
        
        Args:
            api_key: YouTube Data API v3 key
        """
        try:
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError
            self.HttpError = HttpError
        except ImportError:
            raise ImportError(
                "Google API client not installed. Run: pip install google-api-python-client"
            )
        
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def extract_playlist_id(self, playlist_url: str) -> str:
        """
        Extract playlist ID from YouTube URL.
        
        Args:
            playlist_url: YouTube playlist URL
            
        Returns:
            Playlist ID (e.g., "PL7C1_wJG8IAbP9XIvgbiOYvTL3CzS_VMS")
            
        Raises:
            ValueError: If URL doesn't contain a valid playlist ID
        """
        # Parse URL
        parsed = urlparse(playlist_url)
        
        # Try query parameters first (most common)
        if parsed.query:
            params = parse_qs(parsed.query)
            if 'list' in params:
                return params['list'][0]
        
        # Try path-based playlist ID
        match = re.search(r'(?:playlist\?list=|[&?]list=)([a-zA-Z0-9_-]+)', playlist_url)
        if match:
            return match.group(1)
        
        raise ValueError(f"Could not extract playlist ID from URL: {playlist_url}")
    
    def get_playlist_videos(
        self, 
        playlist_id: str, 
        max_results: int = 50,
        include_descriptions: bool = True
    ) -> List[Dict]:
        """
        Fetch all videos from a playlist using YouTube Data API.
        
        Args:
            playlist_id: YouTube playlist ID
            max_results: Results per page (max 50)
            include_descriptions: Fetch full video descriptions
            
        Returns:
            List of video dictionaries with metadata
            
        Raises:
            HttpError: If API request fails
        """
        videos = []
        next_page_token = None
        page_count = 0
        
        print(f"Fetching playlist videos from YouTube API...")
        
        # Fetch all playlist items (paginated)
        while True:
            try:
                request = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=playlist_id,
                    maxResults=max_results,
                    pageToken=next_page_token
                )
                
                response = request.execute()
                page_count += 1
                
                for item in response['items']:
                    snippet = item['snippet']
                    video_id = snippet['resourceId']['videoId']
                    
                    video_data = {
                        'title': snippet['title'],
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'channel': snippet['channelTitle'],
                        'video_id': video_id,
                        'published_at': snippet['publishedAt'],
                        'thumbnail': snippet['thumbnails'].get('medium', {}).get('url', ''),
                    }
                    
                    # Use snippet description if available (limited)
                    if 'description' in snippet:
                        video_data['description'] = snippet['description']
                    
                    videos.append(video_data)
                
                print(f"  Page {page_count}: Fetched {len(response['items'])} videos (Total: {len(videos)})")
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            except self.HttpError as e:
                print(f"API Error: {e}")
                raise
        
        # Optionally fetch full video descriptions (costs more quota)
        if include_descriptions and videos:
            print(f"Fetching detailed video information...")
            videos = self._enrich_video_details(videos)
        
        print(f"✓ Successfully fetched {len(videos)} videos")
        return videos
    
    def _enrich_video_details(self, videos: List[Dict]) -> List[Dict]:
        """
        Fetch additional video details (descriptions, stats).
        
        Args:
            videos: List of basic video data
            
        Returns:
            Enriched video data with full descriptions
        """
        # YouTube API allows up to 50 video IDs per request
        batch_size = 50
        
        for i in range(0, len(videos), batch_size):
            batch = videos[i:i + batch_size]
            video_ids = [v['video_id'] for v in batch]
            
            try:
                request = self.youtube.videos().list(
                    part='snippet,contentDetails,statistics',
                    id=','.join(video_ids)
                )
                
                response = request.execute()
                
                # Map video IDs to enriched data
                enriched_data = {
                    item['id']: item for item in response.get('items', [])
                }
                
                # Update original videos with enriched data
                for video in batch:
                    if video['video_id'] in enriched_data:
                        item = enriched_data[video['video_id']]
                        snippet = item['snippet']
                        
                        # Full description
                        video['description'] = snippet.get('description', '')
                        
                        # Additional metadata
                        if 'contentDetails' in item:
                            video['duration'] = item['contentDetails'].get('duration', '')
                        
                        if 'statistics' in item:
                            stats = item['statistics']
                            video['view_count'] = int(stats.get('viewCount', 0))
                            video['like_count'] = int(stats.get('likeCount', 0))
                        
                        # Tags
                        video['tags'] = snippet.get('tags', [])
                
                print(f"  Enriched {len(batch)} videos (batch {i//batch_size + 1})")
                
            except self.HttpError as e:
                print(f"Warning: Could not enrich batch {i//batch_size + 1}: {e}")
                continue
        
        return videos
    
    def get_playlist_info(self, playlist_id: str) -> Dict:
        """
        Get playlist metadata.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            Playlist information dictionary
        """
        try:
            request = self.youtube.playlists().list(
                part='snippet,contentDetails',
                id=playlist_id
            )
            
            response = request.execute()
            
            if not response.get('items'):
                raise ValueError(f"Playlist not found: {playlist_id}")
            
            item = response['items'][0]
            snippet = item['snippet']
            
            return {
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'channel': snippet['channelTitle'],
                'video_count': item['contentDetails']['itemCount'],
                'published_at': snippet['publishedAt']
            }
            
        except self.HttpError as e:
            print(f"Warning: Could not fetch playlist info: {e}")
            return {}


def test_api():
    """Test the YouTube API extractor."""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python youtube_api_extractor.py <API_KEY> <PLAYLIST_URL>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    playlist_url = sys.argv[2]
    
    extractor = YouTubeAPIExtractor(api_key)
    
    # Extract playlist ID
    playlist_id = extractor.extract_playlist_id(playlist_url)
    print(f"Playlist ID: {playlist_id}")
    
    # Get playlist info
    info = extractor.get_playlist_info(playlist_id)
    print(f"\nPlaylist: {info.get('title', 'Unknown')}")
    print(f"Videos: {info.get('video_count', 0)}")
    
    # Get videos
    videos = extractor.get_playlist_videos(playlist_id, include_descriptions=True)
    
    print(f"\nFirst video:")
    if videos:
        v = videos[0]
        print(f"  Title: {v['title']}")
        print(f"  URL: {v['url']}")
        print(f"  Channel: {v['channel']}")
        print(f"  Description: {v.get('description', 'N/A')[:100]}...")


if __name__ == '__main__':
    test_api()
