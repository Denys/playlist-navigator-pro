
import pytest
import json
import web_app

class TestStoreEndpoints:

    @pytest.fixture
    def client(self):
        web_app.app.config['TESTING'] = True
        # Patch output dir to not restrict to local FS if missing
        web_app.store_api.output_dir = "tests/mock_output"
        return web_app.app.test_client()

    def test_get_categories(self, client):
        res = client.get('/api/store/categories')
        assert res.status_code == 200
        data = json.loads(res.data)
        assert 'categories' in data

    def test_get_filters(self, client):
        res = client.get('/api/store/filters')
        assert res.status_code == 200
        data = json.loads(res.data)
        assert 'genres' in data

    def test_store_search(self, client):
        res = client.get('/api/store/search?q=test')
        assert res.status_code == 200
        data = json.loads(res.data)
        assert 'videos' in data
        assert 'total' in data
