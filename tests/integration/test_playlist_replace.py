import json
import shutil
from pathlib import Path

import pytest

import web_app

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = REPO_ROOT / "tests" / "_runtime_replace"


@pytest.fixture
def replace_runtime(monkeypatch):
    app_root = RUNTIME_ROOT
    shutil.rmtree(app_root, ignore_errors=True)
    output_dir = app_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (app_root / "config.json").write_text(json.dumps({"data_backend": "json"}), encoding="utf-8")

    monkeypatch.setattr(web_app, "get_app_root", lambda: str(app_root))
    web_app._sqlite_store_cache.clear()
    web_app.app.config["TESTING"] = True
    try:
        yield app_root, output_dir
    finally:
        shutil.rmtree(app_root, ignore_errors=True)


def test_register_playlist_overwrite_replaces_old_name_conflict_record(replace_runtime):
    app_root, output_dir = replace_runtime
    old_dir = output_dir / "2604_ai_sel"
    old_dir.mkdir(parents=True, exist_ok=True)
    old_data = old_dir / "old_slug_data.json"
    old_data.write_text(json.dumps([{"video_id": "v-old"}]), encoding="utf-8")
    registry = {
        "playlists": [
            {
                "id": "old_slug",
                "name": "#2604 AI SEL",
                "created_at": "2026-01-01T00:00:00Z",
                "last_updated": "2026-01-01T00:00:00Z",
                "video_count": 13,
                "output_dir": str(old_dir),
                "html_file": str(old_dir / "2604_ai_sel_index.html"),
                "md_file": str(old_dir / "2604_ai_sel_index.md"),
                "color_scheme": "purple",
                "youtube_url": "https://youtube.com/playlist?list=OLDPLAYLIST",
                "folder": "Learning",
            }
        ],
        "total_playlists": 1,
        "total_videos": 13,
    }
    (output_dir / "playlists.json").write_text(json.dumps(registry), encoding="utf-8")

    files = [str(old_dir / "2604_ai_sel_index.md"), str(old_dir / "2604_ai_sel_index.html")]
    web_app.register_playlist(
        "2604 AI SEL",
        str(old_dir),
        files,
        [{"video_id": "v1", "title": "Notion и Claude", "url": "https://youtu.be/v1"}],
        "teal",
        "https://youtube.com/playlist?list=NEWPLAYLIST",
        replace_playlist_id="old_slug",
    )

    saved = json.loads((output_dir / "playlists.json").read_text(encoding="utf-8"))
    assert [p["id"] for p in saved["playlists"]] == ["NEWPLAYLIST"]
    assert saved["playlists"][0]["folder"] == "Learning"
    assert saved["playlists"][0]["video_count"] == 1
    assert not old_data.exists()
    assert (old_dir / "NEWPLAYLIST_data.json").exists()
