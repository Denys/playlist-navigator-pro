
import pytest
import json
from unittest.mock import patch, mock_open
import web_app

class TestWebAppIntegration:
    """Integration tests for web_app.py extensions (Tagging, Dup Detection)."""
    
    @pytest.fixture
    def client(self):
        web_app.app.config['TESTING'] = True
        return web_app.app.test_client()

    @patch('web_app.check_duplicate_playlist')
    def test_duplicate_detection_api(self, mock_check, client):
        """Test that /api/index detects duplicates."""
        mock_check.return_value = {
            'is_duplicate': True,
            'existing_playlist': {'name': 'Existing', 'id': 'existing'}
        }
        
        response = client.post('/api/index', json={
            'playlist_url': 'http://youtube.com/playlist?list=PLExisting',
            'name': 'New Attempt',
            'mode': 'new'
        })
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['is_duplicate'] is True

    @patch('web_app.load_all_videos')
    def test_list_tags(self, mock_load, client):
        """Test tag aggregation API."""
        mock_load.return_value = [
            {'tags': {'youtube_tags': ['yt1'], 'user_defined': ['u1']}},
            {'tags': ['yt2']} # Legacy format check
        ]
        
        response = client.get('/api/tags')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'yt1' in data['youtube_tags']
        assert 'u1' in data['user_defined']
        assert 'yt2' in data['youtube_tags'] # Legacy handling check

    @patch('web_app.load_playlists_registry')
    @patch('web_app.get_data_backend', return_value='json')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"video_id": "v1", "tags": {"user_defined": []}}]')
    @patch('os.path.exists', return_value=True)
    def test_add_user_tag(self, mock_exists, mock_file, mock_backend, mock_registry, client):
        """Test adding a user tag."""
        mock_registry.return_value = {
            'playlists': [{'id': 'p1', 'output_dir': 'output'}]
        }
        
        # We need to mock open explicitly for read/write
        # This is tricky with multiple calls.
        # Simplified: check status code for now with mocked logic flow
        
        response = client.post('/api/videos/v1/tags', json={'tag': '#NewTag'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert '#NewTag' in data['video']['tags']['user_defined']
