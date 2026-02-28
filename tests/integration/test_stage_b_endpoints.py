import json
from pathlib import Path

import pytest

import web_app


@pytest.fixture
def stage_b_client(tmp_path, monkeypatch):
    app_root = tmp_path
    output_dir = app_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (app_root / "config.json").write_text(json.dumps({"data_backend": "json"}), encoding="utf-8")

    playlist_dir = output_dir / "playlist_one"
    playlist_dir.mkdir(parents=True, exist_ok=True)

    registry = {
        "playlists": [
            {
                "id": "p1",
                "name": "Playlist One",
                "created_at": "2026-01-01T00:00:00Z",
                "video_count": 2,
                "output_dir": str(playlist_dir),
                "youtube_url": "https://youtube.com/playlist?list=PL1",
                "folder": None,
            }
        ],
        "total_playlists": 1,
        "total_videos": 2,
    }
    (output_dir / "playlists.json").write_text(json.dumps(registry), encoding="utf-8")

    videos = [
        {
            "video_id": "v1",
            "title": "Python Quickstart",
            "channel": "CodeLab",
            "description": "A beginner friendly Python walkthrough",
            "url": "https://youtu.be/v1",
            "playlist_id": "p1",
            "playlist_name": "Playlist One",
            "tags": {"combined": ["python", "tutorial"]},
        },
        {
            "video_id": "v2",
            "title": "Advanced SQL",
            "channel": "DataLab",
            "description": "Relational indexing deep dive",
            "url": "https://youtu.be/v2",
            "playlist_id": "p1",
            "playlist_name": "Playlist One",
            "tags": {"combined": ["sql", "database"]},
        },
    ]
    (playlist_dir / "p1_data.json").write_text(json.dumps(videos), encoding="utf-8")

    monkeypatch.setattr(web_app, "get_app_root", lambda: str(app_root))
    web_app._sqlite_store_cache.clear()
    web_app.app.config["TESTING"] = True
    return web_app.app.test_client(), output_dir, playlist_dir


def test_search_logic_and_description_toggle(stage_b_client):
    client, _, _ = stage_b_client

    res = client.get("/api/search?q=python+beginner&logic=and&in_description=true")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["total"] == 1
    assert payload["results"][0]["video_id"] == "v1"

    res = client.get("/api/search?q=beginner&logic=or&in_description=false&fields=title,channel,tags")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["total"] == 0

    res = client.get("/api/search?q=beginner&logic=or&in_description=true")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["total"] == 1
    assert payload["results"][0]["video_id"] == "v1"


def test_set_video_notes_persists_json(stage_b_client):
    client, _, playlist_dir = stage_b_client

    res = client.post("/api/videos/v1/notes", json={"notes": "Watch in two sessions"})
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["status"] == "success"
    assert payload["video_id"] == "v1"

    saved = json.loads((playlist_dir / "p1_data.json").read_text(encoding="utf-8"))
    video = next(v for v in saved if v["video_id"] == "v1")
    assert video["notes"] == "Watch in two sessions"


def test_playlist_folder_assignment_and_listing(stage_b_client):
    client, output_dir, _ = stage_b_client

    res = client.post("/api/playlists/p1/folder", json={"folder": "Learning"})
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["status"] == "success"
    assert payload["folder"] == "Learning"

    res = client.get("/api/folders")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["folders"] == [{"name": "Learning", "count": 1}]

    registry = json.loads((output_dir / "playlists.json").read_text(encoding="utf-8"))
    assert registry["playlists"][0]["folder"] == "Learning"


def test_assistant_chat_fallback(stage_b_client):
    client, _, _ = stage_b_client

    res = client.post("/api/assistant/chat", json={})
    assert res.status_code == 400
    assert "error" in res.get_json()

    res = client.post(
        "/api/assistant/chat",
        json={"message": "summarize", "scope": {"query": "python", "limit": 10}},
    )
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["mode"] == "fallback"
    assert payload["sources"] >= 1
    assert "Summary" in payload["answer"]
