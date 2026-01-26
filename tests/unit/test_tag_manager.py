
import pytest
from execution.tag_manager import TagManager
from execution.models import VideoData, TagData, VideoMetadata, ThematicMetadata, GenreMetadata
from datetime import datetime

class TestTagManager:
    
    @pytest.fixture
    def tag_manager(self):
        return TagManager()
    
    @pytest.fixture
    def mock_video(self):
        return VideoData(
            video_id="v1",
            title="Test Video",
            url="http://test",
            channel="Test Channel",
            metadata=VideoMetadata(
                thematic=ThematicMetadata(),
                genre=GenreMetadata()
            ),
            tags=TagData(
                youtube_tags=["yt1", "yt2"],
                auto_generated=["#auto1"],
                user_defined=[],
                combined=["yt1", "yt2", "#auto1"]
            ),
            sync_status={"exists_at_source": True}
        )
        
    def test_add_user_tag(self, tag_manager, mock_video):
        tm = tag_manager
        updated = tm.add_user_tag(mock_video, "#MyTag")
        assert "#MyTag" in updated.tags.user_defined
        assert "#MyTag" in updated.tags.combined
        
    def test_remove_user_tag(self, tag_manager, mock_video):
        tm = tag_manager
        tm.add_user_tag(mock_video, "#Temp")
        updated = tm.remove_user_tag(mock_video, "#Temp")
        assert "#Temp" not in updated.tags.user_defined
        assert "#Temp" not in updated.tags.combined
        
    def test_unique_tags_aggregation(self, tag_manager):
        v1 = VideoData(
            video_id="v1", title="T1", url="u1", channel="c1",
            metadata=VideoMetadata(thematic=ThematicMetadata(), genre=GenreMetadata()),
            tags=TagData(youtube_tags=["y1"], auto_generated=["a1"], combined=["y1", "a1"]),
            sync_status={}
        )
        v2 = VideoData(
            video_id="v2", title="T2", url="u2", channel="c1",
            metadata=VideoMetadata(thematic=ThematicMetadata(), genre=GenreMetadata()),
            tags=TagData(youtube_tags=["y1"], user_defined=["u1"], combined=["y1", "u1"]),
            sync_status={}
        )
        
        all_tags = tag_manager.get_all_unique_tags([[v1, v2]])
        assert "y1" in all_tags['youtube_tags']
        assert "a1" in all_tags['auto_generated']
        assert "u1" in all_tags['user_defined']
        assert len(all_tags['all']) == 3
