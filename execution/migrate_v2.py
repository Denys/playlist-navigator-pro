
import json
import os
from typing import List, Dict, Any
from .metadata_enricher import MetadataEnricher
from .io_utils import utc_now_iso

def migrate_playlist_to_v2(playlist_data: List[Dict[str, Any]], enricher: MetadataEnricher = None) -> List[Dict[str, Any]]:
    """
    Migrates a list of video dictionaries from v1 to v2 schema.
    """
    if enricher is None:
        enricher = MetadataEnricher()
        
    migrated_videos = []
    
    for video in playlist_data:
        # Create shallow copy
        v2_video = video.copy()
        
        # 1. Ensure IDs
        if 'video_id' not in v2_video:
            # Try to extract from URL or something? 
            # Assuming v1 has video_id as per schema
            pass
            
        # 2. Add timestamps if missing
        if 'indexed_at' not in v2_video:
            v2_video['indexed_at'] = utc_now_iso()
        v2_video['last_synced_at'] = utc_now_iso()
        
        # 3. Process duration
        duration_str = v2_video.get('duration', 'PT0S')
        # Use helper from enricher (accessed via protected method or logic duplication)
        # We can just call process_video to do heavy lifting, 
        # BUT we want to preserve existing tags carefully?
        
        # calling enricher.process_video(v2_video) will:
        # - calculate metdata
        # - structure tags
        # - set defaults
        
        # So we can just use that, but we need to ensure 'youtube_tags' get populated from old 'tags'
        # In process_video:
        # existing_tags = tags (which is v2_video.get('tags'))
        # v2_video['tags'] = { 'youtube_tags': existing_tags, ... }
        # This seems correct for migration.
        
        # However, v1 tags might be a mix of user and youtube tags?
        # Current v1 schema: "tags": ["tag1", "tag2"]
        # We don't know which is which. We'll assume they are youtube_tags for now 
        # or just put them in combined.
        # process_video puts them in youtube_tags. That's a safe default.
        
        v2_video = enricher.process_video(v2_video)
        
        # 4. Explicitly ensure sync_status
        if 'sync_status' not in v2_video:
            v2_video['sync_status'] = {
                'exists_at_source': True,
                'last_verified': utc_now_iso()
            }
            
        migrated_videos.append(v2_video)
        
    return migrated_videos

def migrate_file(filepath: str):
    """
    Reads a JSON file, migrates it, and overwrites it (or saves as new).
    """
    if not os.path.exists(filepath):
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Data might be list of dicts directly
    if isinstance(data, list):
        migrated = migrate_playlist_to_v2(data)
        
        # Backup?
        backup_path = filepath + ".bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(migrated, f, indent=2)
            
    print(f"Migrated {filepath}")
