
import pytest
from unittest.mock import MagicMock, patch
from execution.metadata_enricher import MetadataEnricher
from execution.delta_sync import DeltaSync
from execution.models import VideoData
from execution.utils import check_duplicate_playlist

class TestIndexingFlowIntegration:
    """
    Integration tests for the complete indexing flow using the new core components.
    Simulates the process from YouTube API fetch -> Enrichment -> Sync -> Storage.
    """

    @pytest.fixture
    def enricher(self):
        return MetadataEnricher()

    @pytest.fixture
    def delta_sync(self):
        return DeltaSync()

    @pytest.fixture
    def mock_youtube_videos(self):
        return [
            {
                "video_id": "new_vid_1",
                "title": "DIY Synth Build",
                "url": "https://youtu.be/new_vid_1",
                "description": "Building a synth",
                "channel": "Maker",
                "published_at": "2026-01-01T12:00:00Z",
                "tags": ["diy", "synth"],
                "duration": "PT10M"
            },
            {
                "video_id": "new_vid_2",
                "title": "Python Tutorial",
                "url": "https://youtu.be/new_vid_2",
                "description": "Learn Python",
                "channel": "Coder",
                "published_at": "2026-01-02T12:00:00Z",
                "tags": ["python"],
                "duration": "PT20M"
            }
        ]
        
    def test_full_enrichment_flow(self, enricher, mock_youtube_videos):
        """
        Verify raw API data is correctly enriched into v2 schema structure.
        """
        enriched_videos = enricher.process_videos(mock_youtube_videos)
        
        assert len(enriched_videos) == 2
        
        vid1 = enriched_videos[0]
        # Verify schema compliance (using Pydantic model for validation)
        # We try to instantiate the model to ensure it fits
        model_instance = VideoData(**vid1)
        assert model_instance.video_id == "new_vid_1"
        assert model_instance.metadata.thematic.primary == "diy_electronics"
        assert model_instance.metadata.length_category == "medium"
        assert "combined" in vid1['tags']
        assert "#Maker" in vid1['tags']['auto_generated']

    def test_delta_sync_flow(self, enricher, delta_sync, mock_youtube_videos):
        """
        Verify sync flow with existing data, handling updates and new items.
        """
        # 1. First "Scan"
        initial_processed = enricher.process_videos(mock_youtube_videos)
        
        # 2. Simulate User Tagging on existing item
        initial_processed[0]['tags']['user_defined'].append("#UserFav")
        
        # 3. Second "Scan" - One removed, One added, One updated (title)
        fresh_videos = [
            {
                "video_id": "new_vid_1", # Existing
                "title": "DIY Synth Build UPDATED",
                "url": "https://youtu.be/new_vid_1",
                "description": "Building a synth",
                "channel": "Maker",
                "tags": ["diy", "synth"],
                "duration": "PT10M"
            },
            {
                "video_id": "new_vid_3", # New
                "title": "New Video 3",
                "url": "https://youtu.be/new_vid_3",
                "channel": "NewGuy",
                "tags": [],
                "duration": "PT5M"
            }
            # new_vid_2 removed
        ]
        
        # Calculate Delta
        delta = delta_sync.calculate_delta(initial_processed, fresh_videos)
        assert "new_vid_3" in delta['added']
        assert "new_vid_2" in delta['removed']
        assert "new_vid_1" in delta['unchanged']
        
        # Apply Delta
        final_list = delta_sync.apply_delta(initial_processed, fresh_videos, keep_removed=True)
        
        # Verify Results
        vid1 = next(v for v in final_list if v['video_id'] == "new_vid_1")
        vid2 = next(v for v in final_list if v['video_id'] == "new_vid_2")
        vid3 = next(v for v in final_list if v['video_id'] == "new_vid_3")
        
        # 1. Unchanged video should keep user tags
        assert "#UserFav" in vid1['tags']['user_defined']
        # 2. Unchanged video should show updated status
        assert vid1['sync_status']['exists_at_source'] == True
        
        # 3. Removed video should be marked
        assert vid2['sync_status']['exists_at_source'] == False
        
        # 4. New video should be enriched
        assert vid3['metadata']['thematic'] is not None
        assert vid3['sync_status']['exists_at_source'] == True

    def test_duplicate_check_integration(self):
        """
        Verify duplicate detection works with mock registry.
        """
        registry = {
            "playlists": [
                {
                    "id": "my_playlist",
                    "youtube_url": "https://www.youtube.com/playlist?list=PLExistingID"
                }
            ]
        }
        
        # Check Existing
        res = check_duplicate_playlist("https://youtube.com/playlist?list=PLExistingID&feature=share", registry_data=registry)
        assert res['is_duplicate'] is True
        assert res['existing_playlist']['id'] == "my_playlist"
        
        # Check New
        res = check_duplicate_playlist("https://youtube.com/playlist?list=PLNewID", registry_data=registry)
        assert res['is_duplicate'] is False
