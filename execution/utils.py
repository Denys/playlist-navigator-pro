
from urllib.parse import urlparse, parse_qs
import os
import json

def extract_playlist_id_from_url(url: str) -> str:
    """
    Extracts the playlist ID from a YouTube URL.
    Handles standard URLs, mobile URLs, and URLs with extra parameters.
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    
    if 'list' in query:
        return query['list'][0]
    
    return ""

def load_playlists_registry(registry_path: str = "playlists.json") -> dict:
    """Loads the playlist registry file."""
    if not os.path.exists(registry_path):
        return {"playlists": []}
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"playlists": []}

def check_duplicate_playlist(youtube_url: str, registry_data: dict = None) -> dict:
    """
    Checks if a playlist already exists in the registry.
    Returns dict with is_duplicate flag and existing playlist info if found.
    """
    playlist_id = extract_playlist_id_from_url(youtube_url)
    if not playlist_id:
        return {'is_duplicate': False}
        
    if registry_data is None:
        registry_data = load_playlists_registry()
        
    for playlist in registry_data.get('playlists', []):
        existing_url = playlist.get('youtube_url', '')
        # Direct string match or extracting ID from stored URL
        existing_id = extract_playlist_id_from_url(existing_url)
        
        # Also check if stored ID matches (some registries store ID separately)
        if hasattr(playlist, 'get') and playlist.get('id') == playlist_id: # Usually ID is slugified name, not YT ID
             pass # Use YT ID from URL comparison
             
        if existing_id == playlist_id:
            return {
                'is_duplicate': True,
                'existing_playlist': playlist,
                'playlist_id': playlist_id
            }
            
    return {'is_duplicate': False}
