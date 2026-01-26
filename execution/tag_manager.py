
import os
import json
from typing import List, Dict, Set, Optional
from .models import VideoData, TagData

class TagManager:
    """
    Manages user-defined tags and aggregation of all tags.
    Handles persistence of user tags separately or integrated into video data.
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        # We might maintain a sidecar file for user tags if we want them to persist 
        # independent of the main playlist files, OR we rely on modifying the playlist files directly.
        # The Master Plan implies modifying the playlist data files (v2 schema) directly for persistence.
        # But for *global* tag management (autocomplete, browsing), we might want an index.
        pass

    def add_user_tag(self, video: VideoData, tag: str) -> VideoData:
        """
        Add a user-defined tag to a video object.
        """
        if tag not in video.tags.user_defined:
            video.tags.user_defined.append(tag)
            self._update_combined_tags(video)
        return video

    def remove_user_tag(self, video: VideoData, tag: str) -> VideoData:
        """
        Remove a user-defined tag from a video object.
        """
        if tag in video.tags.user_defined:
            video.tags.user_defined.remove(tag)
            self._update_combined_tags(video)
        return video

    def _update_combined_tags(self, video: VideoData):
        """
        Regenerate 'combined' tags list from all sources.
        """
        # Start with youtube tags
        combined = set(video.tags.youtube_tags)
        # Add auto generated
        combined.update(video.tags.auto_generated)
        # Add user defined
        combined.update(video.tags.user_defined)
        
        video.tags.combined = list(combined)

    def get_all_unique_tags(self, playlists_data: List[List[VideoData]]) -> Dict[str, List[str]]:
        """
        Aggregate all unique tags across provided playlists.
        Returns categorized tag lists.
        """
        youtube = set()
        auto = set()
        user = set()
        
        for playlist in playlists_data:
            for video in playlist:
                youtube.update(video.tags.youtube_tags)
                auto.update(video.tags.auto_generated)
                user.update(video.tags.user_defined)
                
        return {
            "youtube_tags": sorted(list(youtube)),
            "auto_generated": sorted(list(auto)),
            "user_defined": sorted(list(user)),
            "all": sorted(list(youtube | auto | user))
        }

    def get_videos_by_tag(self, playlists_data: List[List[VideoData]], tag: str) -> List[VideoData]:
        """
        Find all videos containing a specific tag in any category.
        """
        matches = []
        for playlist in playlists_data:
            for video in playlist:
                if tag in video.tags.combined:
                    matches.append(video)
        return matches
