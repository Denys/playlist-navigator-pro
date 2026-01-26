
import pytest
from execution.migrate_v2 import migrate_playlist_to_v2
from execution.metadata_enricher import MetadataEnricher

class TestMigration:
    
    @pytest.fixture
    def v1_data(self):
        return [
            {
                "title": "Old Video",
                "url": "http://...",
                "video_id": "vid_old",
                "duration": "PT5M",
                "tags": ["old_tag"]
            }
        ]
        
    def test_migrate_adds_metadata_structure(self, v1_data):
        migrated = migrate_playlist_to_v2(v1_data)
        video = migrated[0]
        assert "metadata" in video
        assert "thematic" in video["metadata"]
        assert "sync_status" in video
        
    def test_migrate_preserves_old_tags_as_youtube_tags(self, v1_data):
        migrated = migrate_playlist_to_v2(v1_data)
        video = migrated[0]
        assert "old_tag" in video["tags"]["youtube_tags"]
        assert "old_tag" in video["tags"]["combined"]
        
    def test_migrate_calculates_duration_seconds(self, v1_data):
        migrated = migrate_playlist_to_v2(v1_data)
        video = migrated[0]
        assert video["duration_seconds"] == 300
