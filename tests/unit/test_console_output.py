import builtins
import sys
import types
from pathlib import Path

import pytest

from playlist_indexer import PlaylistIndexer
from youtube_api_extractor import YouTubeAPIExtractor


class FakeRequest:
    def __init__(self, payload):
        self.payload = payload

    def execute(self):
        return self.payload


class FakePlaylistItemsAPI:
    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.calls = 0

    def list(self, **kwargs):
        payload = self.payloads[self.calls]
        self.calls += 1
        return FakeRequest(payload)


class FakeYouTubeSuccess:
    def __init__(self, playlist_payloads):
        self._playlist_items = FakePlaylistItemsAPI(playlist_payloads)

    def playlistItems(self):
        return self._playlist_items


def install_ascii_print(monkeypatch):
    def ascii_strict_print(*args, sep=" ", end="\n", file=None, flush=False):
        message = sep.join(str(arg) for arg in args) + end
        message.encode("cp1252", errors="strict")

    monkeypatch.setattr(builtins, "print", ascii_strict_print)


def write_repo_local_config(dirname: str) -> Path:
    config_dir = Path("test-temproot") / dirname
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.json"
    config_path.write_text('{"youtube_api_key":"test-key"}', encoding="utf-8")
    return config_path


def test_youtube_api_extractor_get_playlist_videos_survives_ascii_stdout(monkeypatch):
    install_ascii_print(monkeypatch)
    extractor = YouTubeAPIExtractor.__new__(YouTubeAPIExtractor)
    extractor.HttpError = RuntimeError
    extractor.youtube = FakeYouTubeSuccess(
        [
            {
                "items": [
                    {
                        "snippet": {
                            "title": "Notion и Claude",
                            "resourceId": {"videoId": "vid1"},
                            "channelTitle": "Bohomolov Lab",
                            "publishedAt": "2026-04-14T00:00:00Z",
                            "thumbnails": {"medium": {"url": "https://example.com/1.jpg"}},
                            "description": "Preview text",
                        },
                        "contentDetails": {},
                    }
                ]
            }
        ]
    )

    videos = extractor.get_playlist_videos("PL123", include_descriptions=False)

    assert [video["video_id"] for video in videos] == ["vid1"]


def test_playlist_indexer_extract_from_youtube_url_survives_ascii_stdout_on_api_success(monkeypatch):
    install_ascii_print(monkeypatch)
    config_path = write_repo_local_config("console_success")

    fake_module = types.ModuleType("youtube_api_extractor")

    class FakeExtractor:
        def __init__(self, api_key):
            assert api_key == "test-key"

        def extract_playlist_id(self, playlist_url):
            return "PL7C1_wJG8IAbqfxQWL9wFlWOMTWVp0POV"

        def get_playlist_info(self, playlist_id):
            return {"title": "2604 AI SEL", "video_count": 14}

        def get_playlist_videos(self, playlist_id, include_descriptions=True):
            return [{"title": "Notion и Claude", "url": "https://www.youtube.com/watch?v=vid1"}]

    fake_module.YouTubeAPIExtractor = FakeExtractor
    monkeypatch.setitem(sys.modules, "youtube_api_extractor", fake_module)

    indexer = PlaylistIndexer(str(config_path))
    videos = indexer.extract_from_youtube_url(
        "https://youtube.com/playlist?list=PL7C1_wJG8IAbqfxQWL9wFlWOMTWVp0POV",
        use_api=True,
    )

    assert [video["title"] for video in videos] == ["Notion и Claude"]


def test_playlist_indexer_fallback_error_path_survives_ascii_stdout(monkeypatch):
    install_ascii_print(monkeypatch)
    config_path = write_repo_local_config("console_fallback")

    fake_module = types.ModuleType("youtube_api_extractor")

    class FakeExtractor:
        def __init__(self, api_key):
            pass

        def extract_playlist_id(self, playlist_url):
            return "PL7C1_wJG8IAbqfxQWL9wFlWOMTWVp0POV"

        def get_playlist_info(self, playlist_id):
            raise RuntimeError("boom")

    fake_module.YouTubeAPIExtractor = FakeExtractor
    monkeypatch.setitem(sys.modules, "youtube_api_extractor", fake_module)

    indexer = PlaylistIndexer(str(config_path))
    with pytest.raises(NotImplementedError):
        indexer.extract_from_youtube_url(
            "https://youtube.com/playlist?list=PL7C1_wJG8IAbqfxQWL9wFlWOMTWVp0POV",
            use_api=True,
        )
