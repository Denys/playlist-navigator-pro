import datetime
import json
import os
import tempfile
from typing import Any


def read_json_file(path: str, default: Any):
    """Read JSON file with a safe fallback."""
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _json_default(obj: Any):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def write_json_atomic(path: str, payload: Any):
    """
    Atomically write JSON by using a temp file + replace.
    This avoids partial/truncated writes when process exits unexpectedly.
    """
    parent = os.path.dirname(path) or "."
    os.makedirs(parent, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_json_", suffix=".json", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            json.dump(payload, tmp, indent=2, ensure_ascii=False, default=_json_default)
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
