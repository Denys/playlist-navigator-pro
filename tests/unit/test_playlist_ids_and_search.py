from pathlib import Path

import web_app


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_build_playlist_record_id_prefers_youtube_playlist_id():
    url = "https://youtube.com/playlist?list=PL7C1_wJG8IAbqfxQWL9wFlWOMTWVp0&si=abc"
    assert web_app.build_playlist_record_id("#2604 AI SEL", url) == "PL7C1_wJG8IAbqfxQWL9wFlWOMTWVp0"


def test_build_playlist_record_id_falls_back_to_slugified_name():
    assert web_app.build_playlist_record_id("#2604 AI SEL", "") == "2604_ai_sel"


def test_filter_video_list_ignores_standalone_plus_token_in_and_queries():
    videos = [
        {
            "title": "Notion и Claude: почему они созданы друг для друга.",
            "channel": "Bohomolov Lab",
            "description": "",
            "tags": [],
        }
    ]

    results = web_app.filter_video_list(
        videos,
        "notion + claude",
        "",
        "",
        logic="and",
        fields=["title", "channel", "tags", "description"],
        in_description=False,
    )

    assert len(results) == 1


def test_frontend_encodes_playlist_ids_in_open_links():
    source = (REPO_ROOT / "static" / "js" / "app.js").read_text(encoding="utf-8")
    assert "encodeURIComponent(el.dataset.openPlaylist)" in source


def test_find_playlist_conflicts_detects_exact_playlist_id_match():
    registry = {
        "playlists": [
            {
                "id": "PL7C1_wJG8IAbqfxQWL9wFlWOMTWVp0POV",
                "name": "2604 AI SEL",
                "youtube_url": "https://youtube.com/playlist?list=PL7C1_wJG8IAbqfxQWL9wFlWOMTWVp0POV",
            }
        ]
    }

    conflict = web_app.find_playlist_conflicts(
        "2604 AI SEL",
        "https://youtube.com/playlist?list=PL7C1_wJG8IAbqfxQWL9wFlWOMTWVp0POV&si=abc",
        registry,
    )

    assert conflict["has_conflict"] is True
    assert conflict["reason"] == "playlist_id"
    assert conflict["recommended_replace_id"] == "PL7C1_wJG8IAbqfxQWL9wFlWOMTWVp0POV"
    assert conflict["exact_id_match"]["name"] == "2604 AI SEL"


def test_find_playlist_conflicts_detects_name_match_with_different_playlist_id():
    registry = {
        "playlists": [
            {
                "id": "old_slug",
                "name": "#2604 AI SEL",
                "youtube_url": "https://youtube.com/playlist?list=OLDPLAYLIST",
            }
        ]
    }

    conflict = web_app.find_playlist_conflicts(
        "2604 AI SEL",
        "https://youtube.com/playlist?list=NEWPLAYLIST",
        registry,
    )

    assert conflict["has_conflict"] is True
    assert conflict["reason"] == "name"
    assert conflict["recommended_replace_id"] == "old_slug"
    assert [p["id"] for p in conflict["name_matches"]] == ["old_slug"]
