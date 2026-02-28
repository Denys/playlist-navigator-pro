import json

import pytest

import web_app
from execution.db import SQLiteStore
from execution.migrate_sqlite import migrate


@pytest.fixture
def sqlite_client(tmp_path, monkeypatch):
    app_root = tmp_path
    output_dir = app_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    db_path = output_dir / "playlist_indexer.db"
    config = {
        "data_backend": "sqlite",
        "sqlite_path": str(db_path),
        "auto_sync": {"enabled": False, "interval_minutes": 60},
    }
    (app_root / "config.json").write_text(json.dumps(config), encoding="utf-8")

    store = SQLiteStore(str(db_path))
    playlist = {
        "id": "p1",
        "name": "Python Path",
        "created_at": "2026-01-01T00:00:00Z",
        "video_count": 3,
        "output_dir": str(output_dir / "p1"),
        "youtube_url": "https://youtube.com/playlist?list=PL1",
        "folder": "Learning",
    }
    store.upsert_playlist(playlist)
    store.save_playlist_videos(
        "p1",
        "Python Path",
        [
            {
                "video_id": "v1",
                "title": "Python Basics for Beginners",
                "channel": "CodeLab",
                "description": "Beginner tutorial for Python",
                "url": "https://youtu.be/v1",
                "duration_seconds": 700,
                "playlist_id": "p1",
                "playlist_name": "Python Path",
                "metadata": {
                    "thematic": {"primary": "programming"},
                    "difficulty_level": "beginner",
                },
                "tags": {"combined": ["python", "beginner", "tutorial"]},
            },
            {
                "video_id": "v2",
                "title": "Intermediate Python Patterns",
                "channel": "CodeLab",
                "description": "Pattern-based Python design",
                "url": "https://youtu.be/v2",
                "duration_seconds": 1200,
                "playlist_id": "p1",
                "playlist_name": "Python Path",
                "metadata": {
                    "thematic": {"primary": "programming"},
                    "difficulty_level": "intermediate",
                },
                "tags": {"combined": ["python", "patterns"]},
            },
            {
                "video_id": "v3",
                "title": "SQL for Data Work",
                "channel": "DataLab",
                "description": "SQL indexing and query tuning",
                "url": "https://youtu.be/v3",
                "duration_seconds": 900,
                "playlist_id": "p1",
                "playlist_name": "Python Path",
                "metadata": {
                    "thematic": {"primary": "programming"},
                    "difficulty_level": "advanced",
                },
                "tags": {"combined": ["sql", "database"]},
            },
        ],
    )

    monkeypatch.setattr(web_app, "get_app_root", lambda: str(app_root))
    web_app._sqlite_store_cache.clear()
    if hasattr(web_app, "sync_scheduler"):
        web_app.sync_scheduler.last_run_at = None
    web_app.app.config["TESTING"] = True
    return web_app.app.test_client()


def test_stage_c_migration_parity(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "playlist_a"
    data_dir.mkdir(parents=True, exist_ok=True)

    registry = {
        "playlists": [
            {
                "id": "pa",
                "name": "Playlist A",
                "created_at": "2026-01-01T00:00:00Z",
                "video_count": 2,
                "output_dir": str(data_dir),
                "youtube_url": "https://youtube.com/playlist?list=PLA",
            }
        ],
        "total_playlists": 1,
        "total_videos": 2,
    }
    (output_dir / "playlists.json").write_text(json.dumps(registry), encoding="utf-8")
    (data_dir / "pa_data.json").write_text(
        json.dumps(
            [
                {"video_id": "a1", "title": "One", "playlist_id": "pa", "playlist_name": "Playlist A"},
                {"video_id": "a2", "title": "Two", "playlist_id": "pa", "playlist_name": "Playlist A"},
            ]
        ),
        encoding="utf-8",
    )

    report = migrate(str(output_dir), str(output_dir / "playlist_indexer.db"), reset=True, dry_run=False)
    assert report["parity_ok"] is True
    assert report["json_total_playlists"] == report["db_total_playlists"] == 1
    assert report["json_total_videos"] == report["db_total_videos"] == 2


def test_stage_d_analytics_endpoint(sqlite_client):
    res = sqlite_client.get("/api/analytics/summary")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["total_playlists"] == 1
    assert payload["total_videos"] == 3
    assert payload["total_watch_time_seconds"] >= 2800


def test_stage_d_scheduler_endpoints(sqlite_client):
    res = sqlite_client.get("/api/scheduler/status")
    assert res.status_code == 200
    status = res.get_json()
    assert "enabled" in status
    assert "interval_minutes" in status

    res = sqlite_client.post("/api/scheduler/config", json={"enabled": True, "interval_minutes": 30})
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["enabled"] is True
    assert payload["interval_minutes"] == 30

    res = sqlite_client.post("/api/scheduler/run-once", json={"dry_run": True})
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["status"] == "success"
    assert payload["dry_run"] is True
    assert payload["playlists_checked"] == 1


def test_stage_e_ai_endpoints(sqlite_client):
    res = sqlite_client.get("/api/ai/summary/v1")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["video_id"] == "v1"
    assert payload["ai_summary"]

    res = sqlite_client.get("/api/ai/suggest-tags/v1")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["video_id"] == "v1"
    assert isinstance(payload["suggested_tags"], list)
    assert payload["suggested_tags"]

    res = sqlite_client.get("/api/ai/recommendations/v1?limit=2")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["video_id"] == "v1"
    assert len(payload["recommendations"]) <= 2

    res = sqlite_client.get("/api/ai/difficulty-path?playlist_id=p1")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["playlist_id"] == "p1"
    assert "beginner" in payload["path"]
