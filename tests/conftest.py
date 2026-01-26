
import pytest
import json
import os
import sys
from datetime import datetime
from io import BytesIO

# Add project root to path so we can import execution modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_video_v1():
    """Legacy v1 schema video fixture."""
    return {
        "title": "DIY Arduino Synthesizer Tutorial",
        "url": "https://www.youtube.com/watch?v=test123_v1",
        "channel": "TechMaker",
        "video_id": "test123_v1",
        "published_at": "2025-06-15T10:00:00Z",
        "thumbnail": "https://i.ytimg.com/vi/test123_v1/mqdefault.jpg",
        "description": "Learn how to build a synthesizer with Arduino",
        "duration": "PT15M30S",
        "view_count": 5000,
        "like_count": 250,
        "tags": ["arduino", "synthesizer", "diy", "tutorial"],
        "playlist_id": "test_playlist",
        "playlist_name": "Test Playlist"
    }

@pytest.fixture
def mock_video_v2():
    """Enhanced v2 schema video fixture."""
    return {
        "video_id": "test123_v2",
        "title": "DIY Arduino Synthesizer Tutorial",
        "url": "https://www.youtube.com/watch?v=test123_v2",
        "channel": "TechMaker",
        "channel_id": "UC_test_channel",
        "published_at": "2025-06-15T10:00:00Z",
        "indexed_at": "2025-12-01T08:00:00Z",
        "last_synced_at": "2025-12-10T12:00:00Z",
        "thumbnail": "https://i.ytimg.com/vi/test123_v2/mqdefault.jpg",
        "description": "Learn how to build a synthesizer with Arduino",
        "duration": "PT15M30S",
        "duration_seconds": 930,
        "view_count": 5000,
        "like_count": 250,
        "metadata": {
            "thematic": {"primary": "diy_electronics", "secondary": ["audio_music"], "confidence": 0.85},
            "genre": {"primary": "Tutorial", "all": ["Tutorial", "Demo"]},
            "author_type": "Creator",
            "length_category": "medium",
            "content_type": "instructional",
            "difficulty_level": "beginner"
        },
        "tags": {
            "youtube_tags": ["arduino", "synthesizer"],
            "auto_generated": ["#DIY", "#Arduino", "#Tutorial"],
            "user_defined": [],
            "combined": ["arduino", "synthesizer", "#DIY", "#Arduino", "#Tutorial"]
        },
        "playlist_memberships": [
            {"playlist_id": "test_playlist", "playlist_name": "Test Playlist", "added_at": "2025-12-01T08:00:00Z"}
        ],
        "sync_status": {"exists_at_source": True, "last_verified": "2025-12-10T12:00:00Z"}
    }

@pytest.fixture
def mock_playlist_registry():
    """Mock playlists.json registry."""
    return {
        "playlists": [
            {
                "id": "test_playlist",
                "name": "Test Playlist",
                "created_at": "2025-12-01T08:00:00Z",
                "video_count": 10,
                "output_dir": "output/test_playlist.json",
                "youtube_url": "https://youtube.com/playlist?list=PLtest123"
            }
        ],
        "total_playlists": 1,
        "total_videos": 10,
        "last_updated": "2025-12-01T08:00:00Z"
    }

@pytest.fixture
def mock_youtube_api_response():
    """Mock YouTube API playlist response."""
    return {
        "items": [
            {
                "snippet": {
                    "title": "New Video Title",
                    "channelTitle": "TechMaker",
                    "publishedAt": "2025-12-15T10:00:00Z",
                    "description": "New video description"
                },
                "contentDetails": {
                    "videoId": "new_vid_001"
                }
            }
        ],
        "pageInfo": {"totalResults": 1}
    }

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory for test isolation."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
