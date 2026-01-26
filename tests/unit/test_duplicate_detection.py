
import pytest
from execution.utils import check_duplicate_playlist, extract_playlist_id_from_url

class TestDuplicateDetection:
    
    def test_extract_playlist_id_standard_url(self):
        """Extract ID from standard playlist URL."""
        url = "https://youtube.com/playlist?list=PLtest123abc"
        assert extract_playlist_id_from_url(url) == "PLtest123abc"
    
    def test_extract_playlist_id_with_extra_params(self):
        """Extract ID from URL with additional parameters."""
        url = "https://youtube.com/playlist?list=PLtest123&si=abc123"
        assert extract_playlist_id_from_url(url) == "PLtest123"
    
    def test_extract_playlist_id_mobile_url(self):
        """Extract ID from mobile URL format."""
        url = "https://m.youtube.com/playlist?list=PLtest123"
        assert extract_playlist_id_from_url(url) == "PLtest123"
    
    def test_check_duplicate_returns_true_for_existing(self, mock_playlist_registry):
        """Should detect existing playlist as duplicate."""
        result = check_duplicate_playlist(
            "https://youtube.com/playlist?list=PLtest123", 
            registry_data=mock_playlist_registry
        )
        assert result["is_duplicate"] == True
        assert result["existing_playlist"]["name"] == "Test Playlist"
    
    def test_check_duplicate_returns_false_for_new(self, mock_playlist_registry):
        """Should not detect new playlist as duplicate."""
        result = check_duplicate_playlist(
            "https://youtube.com/playlist?list=PLnew_playlist",
            registry_data=mock_playlist_registry
        )
        assert result["is_duplicate"] == False
    
    def test_check_duplicate_handles_url_variants(self, mock_playlist_registry):
        """Should match despite URL format differences."""
        # Registry has: https://youtube.com/playlist?list=PLtest123
        # Input has: &si=xyz
        result = check_duplicate_playlist(
            "https://www.youtube.com/playlist?list=PLtest123&si=xyz",
            registry_data=mock_playlist_registry
        )
        assert result["is_duplicate"] == True
