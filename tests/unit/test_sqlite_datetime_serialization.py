import shutil
from datetime import datetime
from pathlib import Path

from execution.db import SQLiteStore


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = REPO_ROOT / "tests" / "_runtime_sqlite"


def test_sqlite_store_serializes_datetime_payloads():
    shutil.rmtree(RUNTIME_ROOT, ignore_errors=True)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    db_path = RUNTIME_ROOT / "playlist_indexer.db"

    store = SQLiteStore(str(db_path))
    store.save_playlist_videos(
        "p1",
        "Playlist One",
        [
            {
                "video_id": "v1",
                "title": "Video One",
                "channel": "Channel",
                "description": "Desc",
                "url": "https://youtu.be/v1",
                "published_at": "2026-01-01T00:00:00Z",
                "duration_seconds": 123,
                "metadata": {"thematic": {"primary": "programming"}},
                "tags": {"combined": ["python"]},
                "sync_status": {
                    "exists_at_source": True,
                    "last_verified": datetime(2026, 1, 1, 12, 0, 0),
                },
            }
        ],
    )

    videos = store.load_playlist_videos("p1")
    assert len(videos) == 1
    assert videos[0]["sync_status"]["last_verified"] == "2026-01-01T12:00:00"

    shutil.rmtree(RUNTIME_ROOT, ignore_errors=True)
