
import pytest

def test_pytest_is_configured():
    """Verify pytest is properly configured."""
    assert True

def test_fixtures_load(mock_video_v1, mock_video_v2):
    """Verify test fixtures load correctly."""
    assert mock_video_v1["video_id"] == "test123_v1"
    assert mock_video_v2["metadata"]["thematic"]["primary"] == "diy_electronics"

def test_temp_directory_creation(temp_output_dir):
    """Verify temp directory fixture works."""
    assert temp_output_dir.exists()
