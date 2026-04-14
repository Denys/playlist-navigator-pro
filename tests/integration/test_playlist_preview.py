import json
import shutil
from pathlib import Path

import pytest

import web_app


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = REPO_ROOT / "tests" / "_runtime_preview"


@pytest.fixture
def preview_client(monkeypatch):
    app_root = RUNTIME_ROOT
    shutil.rmtree(app_root, ignore_errors=True)
    output_dir = app_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (app_root / "config.json").write_text(json.dumps({"data_backend": "json"}), encoding="utf-8")

    monkeypatch.setattr(web_app, "get_app_root", lambda: str(app_root))
    web_app.app.config["TESTING"] = True
    try:
        yield web_app.app.test_client()
    finally:
        shutil.rmtree(app_root, ignore_errors=True)


def test_playlist_preview_endpoint_returns_preview_payload(preview_client, monkeypatch):
    def fake_preview(url):
        assert url == "https://youtube.com/playlist?list=PL123"
        return {
            "playlist_id": "PL123",
            "title": "#2604 AI SEL",
            "channel": "DK_TLL",
            "video_count": 14,
            "sample_videos": [
                {"title": "Notion и Claude", "video_id": "abc", "url": "https://youtu.be/abc"},
                {"title": "Claude Code", "video_id": "def", "url": "https://youtu.be/def"},
                {"title": "Obsidian + AI", "video_id": "ghi", "url": "https://youtu.be/ghi"},
            ],
        }

    monkeypatch.setattr(web_app, "fetch_playlist_preview", fake_preview)

    res = preview_client.post("/api/playlist-preview", json={"playlist_url": "https://youtube.com/playlist?list=PL123"})

    assert res.status_code == 200
    payload = res.get_json()
    assert payload["playlist_id"] == "PL123"
    assert payload["title"] == "#2604 AI SEL"
    assert payload["video_count"] == 14
    assert [v["title"] for v in payload["sample_videos"]] == [
        "Notion и Claude",
        "Claude Code",
        "Obsidian + AI",
    ]


def test_playlist_preview_endpoint_requires_url(preview_client):
    res = preview_client.post("/api/playlist-preview", json={})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_playlist_preview_endpoint_reports_conflict(preview_client, monkeypatch):
    output_dir = Path(web_app.get_app_root()) / "output"
    registry = {
        "playlists": [
            {
                "id": "old_slug",
                "name": "#2604 AI SEL",
                "created_at": "2026-01-01T00:00:00Z",
                "video_count": 13,
                "output_dir": str(output_dir / "2604_ai_sel"),
                "youtube_url": "https://youtube.com/playlist?list=OLDPLAYLIST",
            }
        ]
    }
    (output_dir / "playlists.json").write_text(json.dumps(registry), encoding="utf-8")

    def fake_preview(url):
        return {
            "playlist_id": "NEWPLAYLIST",
            "title": "2604 AI SEL",
            "channel": "DK_TLL",
            "video_count": 14,
            "sample_videos": [],
        }

    monkeypatch.setattr(web_app, "fetch_playlist_preview", fake_preview)

    res = preview_client.post(
        "/api/playlist-preview",
        json={"playlist_url": "https://youtube.com/playlist?list=NEWPLAYLIST", "name": "2604 AI SEL"},
    )

    assert res.status_code == 200
    payload = res.get_json()
    assert payload["conflict"]["has_conflict"] is True
    assert payload["conflict"]["reason"] == "name"
    assert payload["conflict"]["recommended_replace_id"] == "old_slug"


def test_start_indexing_blocks_conflict_without_overwrite(preview_client):
    output_dir = Path(web_app.get_app_root()) / "output"
    registry = {
        "playlists": [
            {
                "id": "old_slug",
                "name": "#2604 AI SEL",
                "created_at": "2026-01-01T00:00:00Z",
                "video_count": 13,
                "output_dir": str(output_dir / "2604_ai_sel"),
                "youtube_url": "https://youtube.com/playlist?list=OLDPLAYLIST",
            }
        ]
    }
    (output_dir / "playlists.json").write_text(json.dumps(registry), encoding="utf-8")

    res = preview_client.post(
        "/api/index",
        json={
            "playlist_url": "https://youtube.com/playlist?list=NEWPLAYLIST",
            "name": "2604 AI SEL",
            "color_scheme": "teal",
            "mode": "new",
        },
    )

    assert res.status_code == 409
    payload = res.get_json()
    assert payload["is_duplicate"] is True
    assert payload["conflict"]["has_conflict"] is True
    assert payload["conflict"]["recommended_replace_id"] == "old_slug"


def test_index_template_contains_preview_controls():
    source = (REPO_ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert "Preview Playlist" in source
    assert 'id="previewPanel"' in source
    assert 'id="previewButton"' in source


def test_frontend_contains_preview_gate_logic():
    source = (REPO_ROOT / "static" / "js" / "app.js").read_text(encoding="utf-8")
    assert "previewPlaylist" in source
    assert "Preview the playlist before indexing." in source
    assert "replace_playlist_id" in source
    assert "Replace Existing Playlist" in source
