import json
from pathlib import Path
import shutil

import pytest

import web_app


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = REPO_ROOT / "tests" / "_runtime_stream"


@pytest.fixture
def stream_client(monkeypatch):
    app_root = RUNTIME_ROOT
    shutil.rmtree(app_root, ignore_errors=True)
    output_dir = app_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (app_root / "config.json").write_text(json.dumps({"data_backend": "json"}), encoding="utf-8")

    monkeypatch.setattr(web_app, "get_app_root", lambda: str(app_root))
    web_app.app.config["TESTING"] = True
    web_app.jobs.clear()
    try:
        yield web_app.app.test_client()
    finally:
        web_app.jobs.clear()
        shutil.rmtree(app_root, ignore_errors=True)


def test_status_stream_sets_sse_resilience_headers(stream_client):
    job = web_app.IndexingJob("job1", "https://youtube.com/playlist?list=PL1", "Test", "green")
    job.status = "complete"
    job.progress = 100
    job.result = []
    web_app.jobs[job.job_id] = job

    res = stream_client.get(f"/api/status/{job.job_id}")

    assert res.status_code == 200
    assert res.headers["Content-Type"].startswith("text/event-stream")
    assert "no-cache" in res.headers.get("Cache-Control", "").lower()
    assert res.headers.get("X-Accel-Buffering") == "no"


def test_service_worker_does_not_cache_status_stream():
    source = (REPO_ROOT / "static" / "sw.js").read_text(encoding="utf-8")

    assert "/api/status/" in source
    assert "event-stream" in source


def test_frontend_does_not_hard_fail_on_first_eventsource_error():
    source = (REPO_ROOT / "static" / "js" / "app.js").read_text(encoding="utf-8")

    assert 'eventSource.close(); showError("Connection lost");' not in source
