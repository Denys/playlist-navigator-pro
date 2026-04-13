import datetime
import json
import os
import tempfile
from typing import Any


_ENV_LOADED_DIRS = set()


def read_json_file(path: str, default: Any):
    """Read JSON file with a safe fallback."""
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def clean_secret_value(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if text in {"YOUR_API_KEY_HERE", "YOUR_KEY_HERE", "CHANGE_ME", "SET_ME"}:
        return ""
    return text


def load_dotenv_if_present(base_dir: str):
    base_dir = os.path.abspath(base_dir)
    if base_dir in _ENV_LOADED_DIRS:
        return
    _ENV_LOADED_DIRS.add(base_dir)

    env_path = os.path.join(base_dir, ".env")
    if not os.path.exists(env_path):
        return

    try:
        with open(env_path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:].strip()
                if "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if not key:
                    continue
                if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                    value = value[1:-1]
                os.environ.setdefault(key, value)
    except OSError:
        return


def get_env_secret(base_dir: str, *names: str) -> str:
    load_dotenv_if_present(base_dir)
    for name in names:
        value = clean_secret_value(os.environ.get(name, ""))
        if value:
            return value
    return ""


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
