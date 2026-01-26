
import pytest
from execution.delta_sync import DeltaSync

class TestDeltaSync:
    
    @pytest.fixture
    def delta_sync(self):
        return DeltaSync()
    
    @pytest.fixture
    def existing_videos(self):
        return [
            {"video_id": "vid001", "title": "Video 1", "view_count": 100},
            {"video_id": "vid002", "title": "Video 2", "view_count": 200},
            {"video_id": "vid003", "title": "Video 3", "view_count": 300}
        ]
    
    @pytest.fixture
    def current_videos(self):
        return [
            {"video_id": "vid002", "title": "Video 2 Updated", "view_count": 250},
            {"video_id": "vid003", "title": "Video 3", "view_count": 300},
            {"video_id": "vid004", "title": "Video 4 NEW", "view_count": 0}
        ]
    
    def test_calculate_delta_identifies_added(self, delta_sync, existing_videos, current_videos):
        """Delta should identify newly added videos."""
        delta = delta_sync.calculate_delta(existing_videos, current_videos)
        assert "vid004" in delta["added"]
    
    def test_calculate_delta_identifies_removed(self, delta_sync, existing_videos, current_videos):
        """Delta should identify removed videos."""
        delta = delta_sync.calculate_delta(existing_videos, current_videos)
        assert "vid001" in delta["removed"]
    
    def test_calculate_delta_identifies_unchanged(self, delta_sync, existing_videos, current_videos):
        """Delta should identify unchanged videos."""
        delta = delta_sync.calculate_delta(existing_videos, current_videos)
        assert "vid002" in delta["unchanged"]
        assert "vid003" in delta["unchanged"]
    
    def test_apply_delta_preserves_user_tags(self, delta_sync):
        """User-defined tags must be preserved during delta sync."""
        existing = [
            {
                "video_id": "vid001",
                "title": "Video 1",
                "tags": {
                    "youtube_tags": ["tag1"],
                    "auto_generated": ["#Auto"],
                    "user_defined": ["#MyTag", "#Important"]
                }
            }
        ]
        # vid001 exists in both (simulating unchanged)
        current = [{"video_id": "vid001", "title": "Video 1"}]
        
        result = delta_sync.apply_delta(existing, current)
        preserved_video = next(v for v in result if v["video_id"] == "vid001")
        assert "#MyTag" in preserved_video["tags"]["user_defined"]
        assert "#Important" in preserved_video["tags"]["user_defined"]
    
    def test_apply_delta_updates_sync_status(self, delta_sync, existing_videos, current_videos):
        """Delta should update sync_status for all videos."""
        result = delta_sync.apply_delta(existing_videos, current_videos)
        for video in result:
            if video["video_id"] in ["vid002", "vid003", "vid004"]:
                assert video["sync_status"]["exists_at_source"] == True
                assert video["sync_status"]["last_verified"] is not None
    
    def test_apply_delta_marks_removed_videos(self, delta_sync, existing_videos, current_videos):
        """Removed videos should be marked as not existing at source."""
        result = delta_sync.apply_delta(existing_videos, current_videos, keep_removed=True)
        removed_video = next((v for v in result if v["video_id"] == "vid001"), None)
        if removed_video:
            assert removed_video["sync_status"]["exists_at_source"] == False
            
    def test_apply_delta_discards_removed_videos_if_requested(self, delta_sync, existing_videos, current_videos):
        """Removed videos should be discarded if keep_removed=False."""
        result = delta_sync.apply_delta(existing_videos, current_videos, keep_removed=False)
        removed_video = next((v for v in result if v["video_id"] == "vid001"), None)
        assert removed_video is None
    
    def test_apply_delta_returns_stats(self, delta_sync, existing_videos, current_videos):
        """Delta application should return statistics."""
        result, stats = delta_sync.apply_delta_with_stats(existing_videos, current_videos)
        assert stats["added"] == 1
        assert stats["removed"] == 1
        assert stats["unchanged"] == 2
        assert stats["total"] == 4 # 2 unchanged + 1 added + 1 removed (kept)
    
    def test_apply_updates_view_count_for_unchanged(self, delta_sync, existing_videos, current_videos):
        """Unchanged videos should have their view counts updated from source."""
        result = delta_sync.apply_delta(existing_videos, current_videos)
        video_2 = next(v for v in result if v['video_id'] == 'vid002')
        assert video_2['view_count'] == 250
