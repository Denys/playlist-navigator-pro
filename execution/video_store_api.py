
import os
import json
from typing import List, Dict, Any, Optional
from .models import VideoData, ThematicCategory, Genre, LengthCategory, AuthorType

class VideoStoreAPI:
    """
    Backend logic for the Video Store Interface.
    Handles advanced search, filtering, and aggregation of video metadata.
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        
    def _load_all_videos(self) -> List[Dict[str, Any]]:
        """
        Load all videos from all playlists.
        """
        registry_path = os.path.join(self.output_dir, "playlists.json")
        all_videos = []
        
        if not os.path.exists(registry_path):
            return []
            
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                
            for playlist in registry.get('playlists', []):
                data_file = os.path.join(playlist.get('output_dir', self.output_dir), f"{playlist['id']}_data.json")
                if os.path.exists(data_file):
                    with open(data_file, 'r', encoding='utf-8') as f:
                        videos = json.load(f)
                        # Enrich with playlist context if needed currently
                        for v in videos:
                            if 'playlist_id' not in v:
                                v['playlist_id'] = playlist['id']
                                v['playlist_name'] = playlist['name']
                        all_videos.extend(videos)
        except Exception as e:
            print(f"Error loading videos: {e}")
            return []
            
        return all_videos

    def get_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all thematic categories with video counts.
        """
        videos = self._load_all_videos()
        counts = {}
        
        # Initialize counts for known enum values
        for theme in ThematicCategory:
            counts[theme.value] = 0
            
        for video in videos:
            metadata = video.get('metadata', {})
            thematic = "unknown"
            if isinstance(metadata, dict):
                thematic_data = metadata.get('thematic', {})
                if isinstance(thematic_data, dict):
                    thematic = thematic_data.get('primary', 'unknown')
                elif isinstance(thematic_data, str):
                    thematic = thematic_data
            
            # Normalize to match enum values if possible
            if thematic in counts:
                counts[thematic] += 1
            else:
                counts.get('unknown', 0) # Fallback
                
        # Format for frontend
        categories = []
        icons = {
            'diy_electronics': '🔧',
            'audio_music': '🎵',
            'programming': '💻',
            'tutorials': '📚',
            'reviews': '⭐',
            'hardware': '🔌',
            'agriculture_science': '🌱',
            'ai_ml': '🤖',
            'unknown': '❓'
        }
        
        for theme, count in counts.items():
            # Skip unknown if count is 0 or maybe show it?
            # Master plan shows them as "sections"
            name_pretty = theme.replace('_', ' ').title()
            # Fix specific names
            if theme == 'diy_electronics': name_pretty = 'DIY Electronics'
            if theme == 'ai_ml': name_pretty = 'AI & ML'
            
            categories.append({
                'id': theme,
                'name': name_pretty,
                'icon': icons.get(theme, '📦'),
                'count': count
            })
            
        return {'categories': categories}

    def get_filter_options(self) -> Dict[str, List[str]]:
        """
        Get all available filter values from the data.
        """
        videos = self._load_all_videos()
        
        genres = set()
        lengths = set()
        authors = set()
        
        for video in videos:
            metadata = video.get('metadata', {})
            if not metadata: continue
            
            # Genre
            g = metadata.get('genre', {}).get('primary')
            if g: genres.add(g)
            
            # Length
            l = metadata.get('length_category')
            if l: lengths.add(l)
            
            # Author
            # Check root or metadata
            a = metadata.get('author_type') or video.get('author_type')
            if a: authors.add(a)
            
        return {
            'genres': sorted(list(genres)),
            'lengths': sorted(list(lengths)), # custom sort?
            'author_types': sorted(list(authors))
        }

    def search_videos(self, 
                     query: str = None, 
                     thematic: str = None, 
                     genre: str = None, 
                     length: str = None, 
                     author_type: str = None, 
                     sort_by: str = 'newest', 
                     page: int = 1, 
                     per_page: int = 24) -> Dict[str, Any]:
        """
        Advanced video search with filters.
        """
        videos = self._load_all_videos()
        filtered = videos
        
        # 1. Filter by Thematic
        if thematic:
            filtered = [v for v in filtered if v.get('metadata', {}).get('thematic', {}).get('primary') == thematic]
            
        # 2. Filter by Genre
        if genre:
            filtered = [v for v in filtered if v.get('metadata', {}).get('genre', {}).get('primary') == genre]
            
        # 3. Filter by Length
        if length:
            filtered = [v for v in filtered if v.get('metadata', {}).get('length_category') == length]
            
        # 4. Filter by Author Type
        if author_type:
            filtered = [v for v in filtered if v.get('metadata', {}).get('author_type') == author_type]
            
        # 5. Text Query
        if query:
            q = query.lower()
            filtered = [v for v in filtered if 
                        q in v.get('title', '').lower() or 
                        q in v.get('channel', '').lower() or
                        q in v.get('description', '').lower() or
                        any(q in tag.lower() for tag in v.get('tags', {}).get('combined', []))]
                        
        # 6. Sorting
        if sort_by == 'newest':
            filtered.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        elif sort_by == 'oldest':
            filtered.sort(key=lambda x: x.get('published_at', ''))
        elif sort_by == 'title':
            filtered.sort(key=lambda x: x.get('title', '').lower())
        elif sort_by == 'duration':
            # Need seconds. Assume duration_seconds is present or ISO
            filtered.sort(key=lambda x: x.get('duration_seconds', 0), reverse=True)
            
        # 7. Pagination
        total = len(filtered)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_videos = filtered[start_idx:end_idx]
        
        return {
            'videos': paginated_videos,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
