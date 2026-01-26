
import pytest
from execution.video_store_api import VideoStoreAPI

class TestVideoStoreAPI:
    
    @pytest.fixture
    def mock_data_dir(self, tmp_path):
        """Create temp directory with mock data."""
        # Setup playlists.json and data files
        import json
        
        d = tmp_path / "output"
        d.mkdir()
        
        registry = {
            "playlists": [
                {"id": "p1", "name": "P1", "output_dir": str(d)}
            ]
        }
        
        videos = [
            {
                "video_id": "v1", 
                "title": "DIY Synth", 
                "published_at": "2023-01-01T12:00:00Z",
                "metadata": {
                    "thematic": {"primary": "diy_electronics"},
                    "genre": {"primary": "Tutorial"},
                    "length_category": "medium",
                    "author_type": "Creator"
                }
            },
            {
                "video_id": "v2", 
                "title": "Python Code", 
                "published_at": "2023-02-01T12:00:00Z",
                "metadata": {
                    "thematic": {"primary": "programming"},
                    "genre": {"primary": "Demo"},
                    "length_category": "short",
                    "author_type": "Educator"
                }
            }
        ]
        
        (d / "playlists.json").write_text(json.dumps(registry), encoding='utf-8')
        (d / "p1_data.json").write_text(json.dumps(videos), encoding='utf-8')
        
        return str(d)
        
    @pytest.fixture
    def store_api(self, mock_data_dir):
        return VideoStoreAPI(output_dir=mock_data_dir)
        
    def test_get_categories(self, store_api):
        cats = store_api.get_categories()
        diy = next(c for c in cats['categories'] if c['id'] == 'diy_electronics')
        prog = next(c for c in cats['categories'] if c['id'] == 'programming')
        
        assert diy['count'] == 1
        assert prog['count'] == 1
        
    def test_get_filter_options(self, store_api):
        opts = store_api.get_filter_options()
        assert "Tutorial" in opts['genres']
        assert "short" in opts['lengths']
        assert "Creator" in opts['author_types']
        
    def test_search_filters(self, store_api):
        # Filter by thematic
        res = store_api.search_videos(thematic="diy_electronics")
        assert len(res['videos']) == 1
        assert res['videos'][0]['title'] == "DIY Synth"
        
        # Filter by genre
        res = store_api.search_videos(genre="Demo")
        assert len(res['videos']) == 1
        assert res['videos'][0]['title'] == "Python Code"
        
    def test_search_sorting(self, store_api):
        res = store_api.search_videos(sort_by="newest")
        # v2 is feb, v1 is jan
        assert res['videos'][0]['video_id'] == "v2"
        
        res = store_api.search_videos(sort_by="oldest")
        assert res['videos'][0]['video_id'] == "v1"
