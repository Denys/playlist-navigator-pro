import web_app
from execution import io_utils
from playlist_indexer import resolve_youtube_api_key


def test_web_app_youtube_api_key_prefers_env_over_config(tmp_path, monkeypatch):
    app_root = tmp_path
    io_utils._ENV_LOADED_DIRS.clear()
    (app_root / "config.json").write_text('{"youtube_api_key": "config-key"}', encoding="utf-8")

    monkeypatch.setattr(web_app, "get_app_root", lambda: str(app_root))
    monkeypatch.setenv("YOUTUBE_API_KEY", "env-key")

    assert web_app.get_youtube_api_key() == "env-key"


def test_playlist_indexer_resolve_youtube_api_key_reads_dotenv(tmp_path, monkeypatch):
    io_utils._ENV_LOADED_DIRS.clear()
    config_path = tmp_path / "config.json"
    dotenv_path = tmp_path / ".env"
    config_path.write_text("{}", encoding="utf-8")
    dotenv_path.write_text("YOUTUBE_API_KEY=dotenv-key\n", encoding="utf-8")
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    monkeypatch.delenv("PLAYLIST_INDEXER_YOUTUBE_API_KEY", raising=False)

    assert resolve_youtube_api_key({}, str(config_path)) == "dotenv-key"
