
from typing import List, Dict, Any, Tuple, Set
from .metadata_enricher import MetadataEnricher
from .io_utils import utc_now_iso

class DeltaSync:
    """
    Handles synchronization between existing local playlist data and fresh YouTube data
    calculated as a delta (diff).
    """
    
    def __init__(self, enricher: MetadataEnricher = None):
        self.enricher = enricher if enricher else MetadataEnricher()

    def calculate_delta(self, existing_videos: List[Dict[str, Any]], current_videos: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        """
        Identify video IDs that are added, removed, or unchanged.
        """
        existing_ids = {v['video_id'] for v in existing_videos}
        current_ids = {v['video_id'] for v in current_videos}
        
        added = current_ids - existing_ids
        removed = existing_ids - current_ids
        unchanged = current_ids & existing_ids
        
        return {
            'added': added,
            'removed': removed,
            'unchanged': unchanged
        }

    def apply_delta(self, existing_videos: List[Dict[str, Any]], current_videos: List[Dict[str, Any]], keep_removed: bool = True) -> List[Dict[str, Any]]:
        """
        Apply delta to produce final video list.
        - Merges new videos (enriched).
        - Preserves existing videos (especially user tags).
        - Updates sync_status for all.
        """
        delta = self.calculate_delta(existing_videos, current_videos)
        
        existing_map = {v['video_id']: v for v in existing_videos}
        # Note: current_videos might not be enriched yet if they come raw from logic
        # But usually current_videos comes from youtube_extractor which has basic metadata
        current_map = {v['video_id']: v for v in current_videos}
        
        final_videos = []
        now_ts = utc_now_iso()
        
        # 1. Process Unchanged
        for vid_id in delta['unchanged']:
            video = existing_map[vid_id]
            # Update sync status
            if 'sync_status' not in video:
                video['sync_status'] = {}
            video['sync_status']['exists_at_source'] = True
            video['sync_status']['last_verified'] = now_ts
            
            # Optionally update mutable fields from source (view_count, etc.)?
            # For now, let's assume we might want to update stats but keep user metadata.
            # But the plan says "Modify: Add new, remove deleted".
            # It also says "Preserve user-defined tags on unchanged videos".
            # Ideally we might want to refresh view counts from current_map data
            new_data = current_map[vid_id]
            video['view_count'] = new_data.get('view_count', video.get('view_count'))
            video['like_count'] = new_data.get('like_count', video.get('like_count'))
            
            final_videos.append(video)
            
        # 2. Process Added
        added_videos_raw = [current_map[vid_id] for vid_id in delta['added']]
        added_videos_enriched = self.enricher.process_videos(added_videos_raw)
        for video in added_videos_enriched:
            # Sync status already set by enricher, but ensure it
            if 'sync_status' not in video:
                video['sync_status'] = {
                    'exists_at_source': True,
                    'last_verified': now_ts
                }
            final_videos.append(video)
            
        # 3. Process Removed
        if keep_removed:
            for vid_id in delta['removed']:
                video = existing_map[vid_id]
                if 'sync_status' not in video:
                    video['sync_status'] = {}
                video['sync_status']['exists_at_source'] = False
                video['sync_status']['last_verified'] = now_ts
                final_videos.append(video)
                
        return final_videos

    def apply_delta_with_stats(self, existing_videos: List[Dict[str, Any]], current_videos: List[Dict[str, Any]], keep_removed: bool = True) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Apply delta and return stats.
        """
        delta = self.calculate_delta(existing_videos, current_videos)
        final_list = self.apply_delta(existing_videos, current_videos, keep_removed)
        
        stats = {
            'added': len(delta['added']),
            'removed': len(delta['removed']),
            'unchanged': len(delta['unchanged']),
            'total': len(final_list)
        }
        return final_list, stats
