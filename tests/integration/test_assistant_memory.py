import json

import pytest

import web_app


@pytest.fixture
def assistant_client(tmp_path, monkeypatch):
    app_root = tmp_path
    output_dir = app_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (app_root / "config.json").write_text(json.dumps({"data_backend": "json"}), encoding="utf-8")
    (output_dir / "playlists.json").write_text(json.dumps({"playlists": []}), encoding="utf-8")

    monkeypatch.setattr(web_app, "get_app_root", lambda: str(app_root))
    web_app.app.config["TESTING"] = True
    return web_app.app.test_client()


def test_assistant_page_route(assistant_client):
    res = assistant_client.get("/assistant")
    assert res.status_code == 200
    assert b"Assistant" in res.data


def test_assistant_history_and_memory_fallback(assistant_client, monkeypatch):
    monkeypatch.setattr(
        web_app,
        "load_all_videos",
        lambda: [
            {
                "video_id": "v1",
                "title": "Python Basics",
                "description": "Beginner Python tutorial",
                "channel": "CodeLab",
                "playlist_name": "P1",
                "tags": {"combined": ["python", "beginner"]},
            }
        ],
    )

    session_id = "memory-test"
    res = assistant_client.post(
        "/api/assistant/llm-chat",
        json={
            "message": "remember my name is Denko",
            "session_id": session_id,
            "scope": {"limit": 20},
        },
    )
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["mode"] == "fallback"
    assert payload["session_id"] == session_id
    assert len(payload["history"]) >= 2
    assert any("my name is Denko" in item for item in payload["memory"]["items"])

    res = assistant_client.get(f"/api/assistant/history?session_id={session_id}")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["session_id"] == session_id
    assert len(payload["history"]) >= 2

    res = assistant_client.delete(f"/api/assistant/history?session_id={session_id}&clear_memory=true")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["status"] == "success"


def test_assistant_llm_mode_with_mocked_provider(assistant_client, monkeypatch):
    monkeypatch.setattr(web_app, "load_all_videos", lambda: [{"video_id": "v1", "title": "T", "description": "D", "channel": "C", "playlist_name": "P"}])
    monkeypatch.setattr(web_app, "_call_openai_chat", lambda *args, **kwargs: "Mocked LLM answer")

    res = assistant_client.post(
        "/api/assistant/llm-chat",
        json={
            "message": "summarize",
            "api_key": "sk-test",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "session_id": "llm-test",
        },
    )
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["mode"] == "llm"
    assert payload["answer"] == "Mocked LLM answer"
    assert payload["session_id"] == "llm-test"


def test_assistant_uses_runtime_defaults_when_payload_omits_provider_model_key(assistant_client, monkeypatch):
    monkeypatch.setattr(
        web_app,
        "load_runtime_config",
        lambda: {
            "data_backend": "json",
            "assistant": {
                "provider": "gemini",
                "model": "gemini-3-flash-preview",
                "api_key": "embedded-key",
            },
        },
    )
    monkeypatch.setattr(
        web_app,
        "load_all_videos",
        lambda: [{"video_id": "v1", "title": "T", "description": "D", "channel": "C", "playlist_name": "P"}],
    )
    seen = {}

    def fake_provider_chat(provider, api_key, model, *_args, **_kwargs):
        seen["provider"] = provider
        seen["api_key"] = api_key
        seen["model"] = model
        return "runtime-defaults-ok"

    monkeypatch.setattr(web_app, "_call_provider_chat", fake_provider_chat)

    res = assistant_client.post(
        "/api/assistant/llm-chat",
        json={
            "message": "test defaults",
            "session_id": "defaults-test",
        },
    )
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["mode"] == "llm"
    assert payload["provider"] == "gemini"
    assert payload["model"] == "gemini-3-flash-preview"
    assert payload["answer"] == "runtime-defaults-ok"
    assert seen["provider"] == "gemini"
    assert seen["api_key"] == "embedded-key"
    assert seen["model"] == "gemini-3-flash-preview"


@pytest.mark.parametrize(
    "provider,model",
    [
        ("openrouter", "openai/gpt-4o-mini"),
        ("anthropic", "claude-3-5-sonnet-latest"),
        ("gemini", "gemini-3-flash-preview"),
    ],
)
def test_assistant_llm_mode_multiprovider_dispatch(assistant_client, monkeypatch, provider, model):
    monkeypatch.setattr(
        web_app,
        "load_all_videos",
        lambda: [{"video_id": "v1", "title": "T", "description": "D", "channel": "C", "playlist_name": "P"}],
    )
    monkeypatch.setattr(web_app, "_call_provider_chat", lambda p, *args, **kwargs: f"{p}-ok")

    res = assistant_client.post(
        "/api/assistant/llm-chat",
        json={
            "message": "test provider",
            "api_key": "sk-test",
            "provider": provider,
            "model": model,
            "session_id": f"{provider}-test",
        },
    )
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["mode"] == "llm"
    assert payload["provider"] == provider
    assert payload["answer"] == f"{provider}-ok"
