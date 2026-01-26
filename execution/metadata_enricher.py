
import re
from datetime import timedelta, datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class ThematicCategory(Enum):
    DIY_ELECTRONICS = "diy_electronics"
    AUDIO_MUSIC = "audio_music"
    PROGRAMMING = "programming"
    TUTORIALS = "tutorials"
    REVIEWS = "reviews"
    HARDWARE = "hardware"
    AGRICULTURE_SCIENCE = "agriculture_science"
    AI_ML = "ai_ml"
    UNKNOWN = "unknown"

class Genre(Enum):
    TUTORIAL = "Tutorial"
    REVIEW = "Review"
    DEMO = "Demo"
    LIVE_SESSION = "Live Session"
    DOCUMENTARY = "Documentary"
    ENTERTAINMENT = "Entertainment"
    UNKNOWN = "Unknown"

class MetadataEnricher:
    """
    Enriches video data with thematic classification, genre detection,
    length categorization, and auto-tagging.
    """
    
    THEMATIC_KEYWORDS = {
        ThematicCategory.DIY_ELECTRONICS: ['diy', 'build', 'solder', 'pcb', 'circuit', 'schematic', 'soldering', 'electronics'],
        ThematicCategory.AUDIO_MUSIC: ['synth', 'audio', 'music', 'midi', 'dsp', 'sound', 'modular', 'eurorack', 'oscillator'],
        ThematicCategory.PROGRAMMING: ['code', 'programming', 'firmware', 'software', 'api', 'python', 'cpp', 'c++', 'arduino', 'github'],
        ThematicCategory.TUTORIALS: ['tutorial', 'guide', 'how to', 'learn', 'lesson', 'course', 'beginner', 'basics'],
        ThematicCategory.REVIEWS: ['review', 'comparison', 'vs', 'test', 'analysis', 'thoughts', 'opinion'],
        ThematicCategory.HARDWARE: ['hardware', 'microcontroller', 'arduino', 'teensy', 'daisy', 'stm32', 'esp32', 'raspberry pi'],
        ThematicCategory.AGRICULTURE_SCIENCE: ['soil', 'plant', 'weather', 'sensor', 'monitoring', 'garden', 'hydroponics'],
        ThematicCategory.AI_ML: ['ai', 'llm', 'machine learning', 'neural', 'gpt', 'transformer', 'model', 'inference']
    }
    
    GENRE_PATTERNS = {
        Genre.TUTORIAL: [r'how to', r'tutorial', r'guide', r'learn', r'basics', r'101', r'lesson'],
        Genre.REVIEW: [r'review', r'vs\.?', r'comparison', r'thoughts on'],
        Genre.DEMO: [r'demo', r'demonstration', r'showcase', r'walkthrough', r'jam', r'test'],
        Genre.LIVE_SESSION: [r'live', r'stream', r'workshop', r'webinar', r'q&a'],
        Genre.DOCUMENTARY: [r'documentary', r'history', r'journey', r'story of', r'behind the scenes'],
    }
    
    def classify_thematic(self, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        """
        Classify video into primary and secondary thematic categories based on
        keywords in title, description, and tags.
        """
        text = (f"{title} {description} {' '.join(tags)}").lower()
        scores = {category: 0 for category in ThematicCategory if category != ThematicCategory.UNKNOWN}
        
        for category, keywords in self.THEMATIC_KEYWORDS.items():
            for keyword in keywords:
                # Simple keyword matching (could be regex for better accuracy)
                # Give more weight to title and tags
                count = 0
                if keyword in title.lower():
                    count += 3
                if keyword in [t.lower() for t in tags]:
                    count += 2
                if keyword in description.lower():
                    count += 1
                scores[category] += count
        
        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_category = sorted_scores[0][0] if sorted_scores[0][1] > 0 else ThematicCategory.UNKNOWN
        
        # Get secondary categories (with some score threshold, e.g., > 2)
        secondary_categories = [cat.value for cat, score in sorted_scores[1:] if score > 2]
        
        # Calculate naive confidence score (normalized by top score)
        top_score = sorted_scores[0][1]
        confidence = 0.0
        if top_score > 0:
            confidence = min(1.0, top_score / 10.0) # Arbitrary scaling
            
        return {
            "primary": primary_category.value,
            "secondary": secondary_categories,
            "confidence": round(confidence, 2)
        }

    def classify_genre(self, title: str, description: str) -> Dict[str, Any]:
        """
        Determine genre based on title and description patterns.
        """
        title_lower = title.lower()
        desc_lower = description.lower()
        
        found_genre = Genre.UNKNOWN
        all_genres = []
        
        for genre, patterns in self.GENRE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, title_lower) or re.search(pattern, desc_lower):
                    if genre not in all_genres:
                        all_genres.append(genre.value)
                    if found_genre == Genre.UNKNOWN:
                        found_genre = genre # First match is primary? Or prioritize?
                    break
        
        # Default to Entertainment if nothing else found? Or just Unknown.
        # Let's keep Unknown.
        
        return {
            "primary": found_genre.value,
            "all": all_genres
        }

    def categorize_length(self, duration_seconds: int) -> str:
        """
        Categorize video length.
        """
        if duration_seconds < 300: # 5 mins
            return 'short'
        elif duration_seconds < 1200: # 20 mins
            return 'medium'
        elif duration_seconds < 3600: # 60 mins
            return 'long'
        else:
            return 'extended'

    def classify_author(self, channel: str, description: str) -> str:
        """
        Classify author type (simplified heuristic).
        """
        text = (channel + " " + description).lower()
        
        if any(w in text for w in ['official', 'company', 'brand', 'systems', 'corp']):
            return 'Brand'
        if any(w in text for w in ['course', 'lecture', 'professor', 'university', 'academy']):
            return 'Educator'
        if any(w in text for w in ['community', 'meetup', 'conference']):
            return 'Community'
        
        # Default to Creator
        return 'Creator'

    def generate_auto_tags(self, video: Dict[str, Any]) -> List[str]:
        """
        Generate hashtags based on classification.
        """
        tags = []
        
        # Add metadata based tags
        if video.get('metadata'):
            meta = video['metadata']
            if meta.get('thematic') and meta['thematic']['primary'] != 'unknown':
                tags.append(f"#{meta['thematic']['primary'].replace('_', '')}")
            if meta.get('genre') and meta['genre']['primary'] != 'Unknown':
                tags.append(f"#{meta['genre']['primary'].replace(' ', '')}")
            if meta.get('length_category'):
                tags.append(f"#{meta['length_category']}")
        
        # Add channel tag
        channel = video.get('channel', '').replace(' ', '')
        if channel:
            tags.append(f"#{channel}")
            
        return list(set(tags))

    def _parse_duration(self, duration_str: str) -> int:
        """
        Parse ISO8601 duration to seconds.
        Simple parser for PT#M#S format usually returned by YouTube API wrapper
        BUT input might already be parsed or in different format depending on youtube_api_extractor.
        Let's assume the 'duration' field in input video dict is ISO string like PT15M30S.
        """
        # Note: In a real scenario, use isodate library. Here implementing simple regex.
        # Matches PT1H2M3S etc.
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration_str)
        if not match:
            return 0
        
        h, m, s = match.groups()
        hours = int(h) if h else 0
        minutes = int(m) if m else 0
        seconds = int(s) if s else 0
        
        return hours * 3600 + minutes * 60 + seconds

    def process_video(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a single video object with v2 schema metadata.
        """
        # Create a copy to avoid mutating input directly if not desired
        v2_video = video.copy()
        
        # Ensure v2 fields exist
        if 'title' not in v2_video: v2_video['title'] = ""
        if 'description' not in v2_video: v2_video['description'] = ""
        tags = v2_video.get('tags', [])
        if not isinstance(tags, list): tags = []
        
        # Calculate derived fields
        duration_str = v2_video.get('duration', 'PT0S')
        duration_seconds = self._parse_duration(duration_str)
        v2_video['duration_seconds'] = duration_seconds
        
        # Metadata classification
        metadata = {}
        metadata['thematic'] = self.classify_thematic(v2_video['title'], v2_video['description'], tags)
        metadata['genre'] = self.classify_genre(v2_video['title'], v2_video['description'])
        metadata['author_type'] = self.classify_author(v2_video.get('channel', ''), v2_video['description'])
        metadata['length_category'] = self.categorize_length(duration_seconds)
        # Default others
        metadata['content_type'] = 'video'
        metadata['difficulty_level'] = 'intermediate'
        
        v2_video['metadata'] = metadata
        
        # Tags structure
        auto_tags = self.generate_auto_tags(v2_video)
        existing_tags = tags
        
        v2_video['tags'] = {
            'youtube_tags': existing_tags,
            'auto_generated': auto_tags,
            'user_defined': [],
            'combined': list(set(existing_tags + auto_tags)) # user_defined empty initially
        }
        
        # Sync status defaults for new items
        if 'sync_status' not in v2_video:
            v2_video['sync_status'] = {
                'exists_at_source': True,
                'last_verified': datetime.utcnow()
            }
        
        # Ensure optional fields are present for Pydantic if missing
        for field in ['view_count', 'like_count', 'duration_seconds']:
            if field not in v2_video:
                v2_video[field] = 0
                
        return v2_video

    def process_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch process videos."""
        return [self.process_video(v) for v in videos]
