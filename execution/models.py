
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional, Dict, Union
from datetime import datetime
from enum import Enum

class ThematicCategory(str, Enum):
    DIY_ELECTRONICS = "diy_electronics"
    AUDIO_MUSIC = "audio_music"
    PROGRAMMING = "programming"
    TUTORIALS = "tutorials"
    REVIEWS = "reviews"
    HARDWARE = "hardware"
    AGRICULTURE_SCIENCE = "agriculture_science"
    AI_ML = "ai_ml"
    UNKNOWN = "unknown"

class Genre(str, Enum):
    TUTORIAL = "Tutorial"
    REVIEW = "Review"
    DEMO = "Demo"
    LIVE_SESSION = "Live Session"
    DOCUMENTARY = "Documentary"
    ENTERTAINMENT = "Entertainment"
    UNKNOWN = "Unknown"

class AuthorType(str, Enum):
    CREATOR = "Creator"
    EDUCATOR = "Educator"
    BRAND = "Brand"
    COMMUNITY = "Community"
    EXPERT = "Expert"
    UNKNOWN = "Unknown"

class LengthCategory(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    EXTENDED = "extended"
    UNKNOWN = "unknown"

class ThematicMetadata(BaseModel):
    primary: ThematicCategory = ThematicCategory.UNKNOWN
    secondary: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

class GenreMetadata(BaseModel):
    primary: Genre = Genre.UNKNOWN
    all: List[str] = Field(default_factory=list)

class TagData(BaseModel):
    youtube_tags: List[str] = Field(default_factory=list)
    auto_generated: List[str] = Field(default_factory=list)
    user_defined: List[str] = Field(default_factory=list)
    combined: List[str] = Field(default_factory=list)

class SyncStatus(BaseModel):
    exists_at_source: bool = True
    last_verified: datetime = Field(default_factory=datetime.utcnow)

class PlaylistMembership(BaseModel):
    playlist_id: str
    playlist_name: str
    added_at: datetime = Field(default_factory=datetime.utcnow)

class VideoMetadata(BaseModel):
    thematic: ThematicMetadata
    genre: GenreMetadata
    author_type: AuthorType = AuthorType.UNKNOWN
    length_category: LengthCategory = LengthCategory.UNKNOWN
    content_type: str = "video"
    difficulty_level: str = "intermediate"

class VideoData(BaseModel):
    video_id: str
    title: str
    url: str
    channel: str
    channel_id: Optional[str] = None
    published_at: Optional[str] = None # ISO string
    indexed_at: datetime = Field(default_factory=datetime.utcnow)
    last_synced_at: datetime = Field(default_factory=datetime.utcnow)
    thumbnail: Optional[str] = None
    description: str = ""
    duration: Optional[str] = None # ISO format PT15M
    duration_seconds: int = 0
    view_count: Optional[int] = 0
    like_count: Optional[int] = 0
    
    metadata: VideoMetadata
    tags: TagData
    
    playlist_memberships: List[PlaylistMembership] = Field(default_factory=list)
    sync_status: SyncStatus
    
    class Config:
        arbitrary_types_allowed = True
        extra = "ignore" 
