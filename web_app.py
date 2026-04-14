#!/usr/bin/env python3
"""
Unified Playlist Manager Web Application
Combines YouTube Playlist Indexer and Master Search in one tabbed interface.
"""

from flask import Flask, render_template, request, jsonify, Response
from threading import Thread, Event, Lock
import datetime
import uuid
import time
import sys
import os
import json
import urllib.request
import urllib.error
from io import BytesIO # Added as per instruction
from typing import List, Dict, Union, Any, Optional
import re
from playlist_indexer import PlaylistIndexer
from execution.metadata_enricher import MetadataEnricher
from execution.delta_sync import DeltaSync
from execution.tag_manager import TagManager
from execution.video_store_api import VideoStoreAPI
from execution.utils import extract_playlist_id_from_url
from execution.models import VideoData
from execution.io_utils import clean_secret_value, get_env_secret, read_json_file, write_json_atomic, utc_now_iso
from execution.db import SQLiteStore



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if getattr(sys, 'frozen', False):
    # Running in a bundle
    template_folder = resource_path('templates')
    static_folder = resource_path('static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    # Running in normal Python environment
    app = Flask(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder # For Flask < 2.2 compatibility (optional but good)


def get_app_root():
    """Get the application root directory."""
    if getattr(sys, 'frozen', False):
        # If frozen (exe), save next to the executable
        return os.path.dirname(sys.executable)
    else:
        # If dev, save in current working directory
        return os.getcwd()

def get_config_path():
    """Get absolute path to config.json."""
    return os.path.join(get_app_root(), 'config.json')


def load_runtime_config() -> Dict[str, Any]:
    """Load runtime config with safe fallback."""
    cfg = read_json_file(get_config_path(), {})
    return cfg if isinstance(cfg, dict) else {}


def get_youtube_api_key(runtime_cfg: Optional[Dict[str, Any]] = None) -> str:
    cfg = runtime_cfg if isinstance(runtime_cfg, dict) else load_runtime_config()
    env_key = get_env_secret(get_app_root(), "PLAYLIST_INDEXER_YOUTUBE_API_KEY", "YOUTUBE_API_KEY")
    if env_key:
        return env_key
    return clean_secret_value(cfg.get("youtube_api_key", ""))


def get_data_backend() -> str:
    """Current data backend mode: json | sqlite."""
    backend = str(load_runtime_config().get("data_backend", "sqlite")).strip().lower()
    return backend if backend in {"json", "sqlite"} else "sqlite"


def fetch_playlist_preview(playlist_url: str) -> Dict[str, Any]:
    playlist_url = str(playlist_url or "").strip()
    if not playlist_url:
        raise ValueError("playlist_url is required")

    api_key = get_youtube_api_key()
    if not api_key:
        raise ValueError("YouTube API key is not configured")

    from youtube_api_extractor import YouTubeAPIExtractor

    extractor = YouTubeAPIExtractor(api_key)
    playlist_id = extractor.extract_playlist_id(playlist_url)
    info = extractor.get_playlist_info(playlist_id)
    request = extractor.youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults=3,
    )
    response = request.execute()

    sample_videos = []
    for item in response.get("items", []):
        snippet = item.get("snippet", {})
        resource = snippet.get("resourceId", {})
        content = item.get("contentDetails", {})
        video_id = resource.get("videoId") or content.get("videoId") or ""
        sample_videos.append({
            "title": snippet.get("title", ""),
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
            "channel": snippet.get("channelTitle", ""),
        })

    return {
        "playlist_id": playlist_id,
        "title": info.get("title", ""),
        "channel": info.get("channel", ""),
        "video_count": int(info.get("video_count", 0) or 0),
        "sample_videos": sample_videos,
    }


def save_runtime_config(config_data: Dict[str, Any]):
    """Persist runtime config atomically."""
    write_json_atomic(get_config_path(), config_data)


def get_auto_sync_config() -> Dict[str, Any]:
    cfg = load_runtime_config()
    auto_sync = cfg.get("auto_sync")
    if not isinstance(auto_sync, dict):
        auto_sync = {}
    interval = auto_sync.get("interval_minutes", 60)
    try:
        interval = int(interval)
    except (TypeError, ValueError):
        interval = 60
    interval = max(5, min(interval, 1440))
    return {
        "enabled": bool(auto_sync.get("enabled", False)),
        "interval_minutes": interval,
    }


def get_sqlite_path() -> str:
    cfg = load_runtime_config()
    value = cfg.get("sqlite_path")
    if isinstance(value, str) and value.strip():
        if os.path.isabs(value):
            return value
        return os.path.join(get_app_root(), value)
    return os.path.join(get_app_root(), "output", "playlist_indexer.db")


def _to_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


_sqlite_store_cache: Dict[str, SQLiteStore] = {}
_sqlite_bootstrap_done: Dict[str, bool] = {}


def bootstrap_sqlite_from_json_if_needed(store: SQLiteStore, db_path: str):
    """
    If SQLite is empty but JSON registry exists, seed SQLite once from JSON.
    This prevents empty UI when users switch default backend to SQLite
    before running an explicit migration command.
    """
    if _sqlite_bootstrap_done.get(db_path):
        return
    _sqlite_bootstrap_done[db_path] = True

    # Avoid side effects in test mode where fixtures control storage explicitly.
    if app.config.get("TESTING"):
        return

    try:
        sqlite_registry = store.load_registry()
        if int(sqlite_registry.get("total_playlists", 0) or 0) > 0:
            return

        json_registry = read_json_file(get_registry_path(), {"playlists": []})
        playlists = json_registry.get("playlists", []) if isinstance(json_registry, dict) else []
        if not playlists:
            return

        for p in playlists:
            videos = load_playlist_videos_json(p)
            p_copy = dict(p)
            p_copy["video_count"] = len(videos)
            if not p_copy.get("last_updated"):
                p_copy["last_updated"] = utc_now_iso(z_suffix=True)
            store.upsert_playlist(p_copy)
            store.save_playlist_videos(p_copy.get("id", ""), p_copy.get("name", ""), videos)
    except Exception:
        # Bootstrap failure should not crash app startup.
        pass


def get_sqlite_store() -> SQLiteStore:
    db_path = get_sqlite_path()
    store = _sqlite_store_cache.get(db_path)
    if store is None:
        store = SQLiteStore(db_path)
        _sqlite_store_cache.clear()
        _sqlite_store_cache[db_path] = store
    bootstrap_sqlite_from_json_if_needed(store, db_path)
    return store


def get_registry_path() -> str:
    return os.path.join(get_app_root(), "output", "playlists.json")


def write_registry_json(registry: Dict[str, Any]):
    write_json_atomic(get_registry_path(), registry)


def get_assistant_memory_path() -> str:
    return os.path.join(get_app_root(), "output", "assistant_memory.json")


def get_assistant_runtime_defaults() -> Dict[str, str]:
    """Resolve assistant provider/model/api_key defaults from env + runtime config."""
    cfg = load_runtime_config()
    assistant_cfg = cfg.get("assistant", {}) if isinstance(cfg, dict) else {}
    if not isinstance(assistant_cfg, dict):
        assistant_cfg = {}

    provider = str(assistant_cfg.get("provider", "gemini")).strip().lower() or "gemini"
    provider_model_defaults = {
        "openai": "gpt-4o-mini",
        "openrouter": "openai/gpt-4o-mini",
        "anthropic": "claude-3-5-sonnet-latest",
        "gemini": "gemini-3-flash-preview",
    }
    model = str(
        assistant_cfg.get("model", provider_model_defaults.get(provider, "gemini-3-flash-preview"))
    ).strip() or provider_model_defaults.get(provider, "gemini-3-flash-preview")
    provider_env_names = {
        "openai": ("OPENAI_API_KEY",),
        "openrouter": ("OPENROUTER_API_KEY",),
        "anthropic": ("ANTHROPIC_API_KEY",),
        "gemini": ("GEMINI_API_KEY",),
    }
    api_key = get_env_secret(
        get_app_root(),
        *(provider_env_names.get(provider, ()) + ("PLAYLIST_INDEXER_ASSISTANT_API_KEY",)),
    )
    if not api_key:
        api_key = clean_secret_value(assistant_cfg.get("api_key", ""))
    return {"provider": provider, "model": model, "api_key": api_key}


def load_assistant_memory_store() -> Dict[str, Any]:
    store = read_json_file(get_assistant_memory_path(), {"conversations": {}, "memory": {"items": [], "updated_at": None}})
    if not isinstance(store, dict):
        store = {"conversations": {}, "memory": {"items": [], "updated_at": None}}
    if not isinstance(store.get("conversations"), dict):
        store["conversations"] = {}
    if not isinstance(store.get("memory"), dict):
        store["memory"] = {"items": [], "updated_at": None}
    if not isinstance(store["memory"].get("items"), list):
        store["memory"]["items"] = []
    return store


def save_assistant_memory_store(store: Dict[str, Any]):
    write_json_atomic(get_assistant_memory_path(), store)


def _memory_extract_items(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    lowered = text.lower()
    items: List[str] = []
    if lowered.startswith("remember "):
        items.append(text[9:].strip())
    for marker in ["my name is ", "i prefer ", "i like ", "i work on "]:
        idx = lowered.find(marker)
        if idx >= 0:
            snippet = text[idx: idx + 140].strip()
            if snippet:
                items.append(snippet)
    return [i for i in items if i]


def append_assistant_history(session_id: str, role: str, content: str):
    store = load_assistant_memory_store()
    convs = store["conversations"]
    history = convs.get(session_id, [])
    if not isinstance(history, list):
        history = []
    history.append({
        "role": role,
        "content": content,
        "ts": utc_now_iso(z_suffix=True),
    })
    # Keep bounded history size per session.
    convs[session_id] = history[-120:]

    new_memory_items = _memory_extract_items(content) if role == "user" else []
    if new_memory_items:
        existing = store["memory"].get("items", [])
        for item in new_memory_items:
            if item not in existing:
                existing.append(item)
        store["memory"]["items"] = existing[-200:]
        store["memory"]["updated_at"] = utc_now_iso(z_suffix=True)
    save_assistant_memory_store(store)


def get_assistant_history(session_id: str) -> List[Dict[str, Any]]:
    store = load_assistant_memory_store()
    history = store["conversations"].get(session_id, [])
    return history if isinstance(history, list) else []


def load_playlist_videos_json(playlist: Dict[str, Any]) -> List[Dict[str, Any]]:
    data_file = os.path.join(playlist.get("output_dir", ""), f"{playlist.get('id', '')}_data.json")
    if not data_file:
        return []
    return read_json_file(data_file, [])


def save_playlist_videos_json(playlist: Dict[str, Any], videos: List[Dict[str, Any]]):
    data_file = os.path.join(playlist.get("output_dir", ""), f"{playlist.get('id', '')}_data.json")
    if data_file:
        write_json_atomic(data_file, videos)


def load_playlist_videos(playlist: Dict[str, Any]) -> List[Dict[str, Any]]:
    if get_data_backend() == "sqlite":
        return get_sqlite_store().load_playlist_videos(playlist.get("id", ""))
    return load_playlist_videos_json(playlist)


def save_playlist_videos(playlist: Dict[str, Any], videos: List[Dict[str, Any]]):
    if get_data_backend() == "sqlite":
        get_sqlite_store().save_playlist_videos(playlist.get("id", ""), playlist.get("name", ""), videos)
        return
    save_playlist_videos_json(playlist, videos)

# Job tracking for indexing
jobs = {}
enricher = MetadataEnricher()
delta_sync = DeltaSync(enricher)
tag_manager = TagManager()
store_api = VideoStoreAPI(output_dir=os.path.join(get_app_root(), 'output'))


class AutoSyncScheduler:
    """Minimal in-process scheduler for periodic sync operations."""

    def __init__(self):
        self.enabled = False
        self.interval_minutes = 60
        self.last_run_at: Optional[str] = None
        self.last_result: Dict[str, Any] = {}
        self._thread: Optional[Thread] = None
        self._stop_event = Event()
        self._lock = Lock()

    def configure(self, enabled: bool, interval_minutes: int):
        with self._lock:
            self.enabled = bool(enabled)
            self.interval_minutes = max(5, min(int(interval_minutes), 1440))
        if self.enabled:
            self.start()
        else:
            self.stop()

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._thread = Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()

    def status(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "interval_minutes": self.interval_minutes,
            "last_run_at": self.last_run_at,
            "running": bool(self._thread and self._thread.is_alive()),
            "last_result": self.last_result,
        }

    def run_once(self, dry_run: bool = False) -> Dict[str, Any]:
        return run_auto_sync_once(dry_run=dry_run)

    def _run_loop(self):
        while not self._stop_event.is_set():
            if self.enabled:
                result = run_auto_sync_once(dry_run=False)
                self.last_run_at = utc_now_iso(z_suffix=True)
                self.last_result = result
            wait_seconds = self.interval_minutes * 60
            if self._stop_event.wait(wait_seconds):
                break


sync_scheduler = AutoSyncScheduler()
initial_auto_sync = get_auto_sync_config()
sync_scheduler.enabled = initial_auto_sync["enabled"]
sync_scheduler.interval_minutes = initial_auto_sync["interval_minutes"]




class IndexingJob:
    """Track indexing job progress."""
    def __init__(self, job_id, playlist_url, name, color_scheme):
        self.job_id = job_id
        self.playlist_url = playlist_url
        self.name = name
        self.color_scheme = color_scheme
        self.status = "queued"
        self.progress = 0
        self.message = "Waiting to start..."
        self.result = None
        self.error = None
        self.quota_used = 0


@app.route('/')
def index():
    """Serve the unified interface."""
    return render_template('index.html')


@app.route('/assistant')
def assistant_page():
    """Dedicated assistant page with chat + API key controls."""
    return render_template('assistant.html')


@app.route('/sw.js')
def service_worker():
    """Serve service worker from root scope (required for PWA)."""
    response = app.send_static_file('sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/offline')
def offline():
    """Serve offline fallback page."""
    return render_template('offline.html')


@app.route('/favicon.ico')
def favicon():
    """Serve favicon from PWA icons."""
    return app.send_static_file('icons/icon-192.png')


@app.route('/liquid-demo')
def liquid_demo():
    """Serve the Liquid Dynamics design system demo."""
    return render_template('liquid-demo.html')


@app.route('/api/index', methods=['POST'])
def start_indexing():
    """Start a new indexing job."""
    data = request.json
    
    if not data.get('playlist_url') or not data.get('name'):
        return jsonify({'error': 'Missing playlist_url or name'}), 400
        
    mode = data.get('mode', 'new')
    registry = load_playlists_registry()
    conflict = find_playlist_conflicts(data.get("name", ""), data["playlist_url"], registry)
    replace_playlist_id = str(data.get("replace_playlist_id") or "").strip() or None

    if mode == 'new' and conflict['has_conflict']:
        existing_playlist = conflict.get("exact_id_match")
        if existing_playlist is None and len(conflict.get("name_matches", [])) == 1:
            existing_playlist = conflict["name_matches"][0]
        return jsonify({
            'error': 'Playlist already exists. Choose replace or rename the playlist.',
            'is_duplicate': True,
            'existing_playlist': existing_playlist,
            'conflict': conflict,
        }), 409

    if mode == 'overwrite':
        if replace_playlist_id is None:
            replace_playlist_id = conflict.get("recommended_replace_id")
        if replace_playlist_id is not None:
            target = next((p for p in registry.get("playlists", []) if p.get("id") == replace_playlist_id), None)
            if not target:
                return jsonify({'error': 'replace_playlist_id not found'}), 400
    
    job_id = str(uuid.uuid4())[:8]
    job = IndexingJob(
        job_id,
        data['playlist_url'],
        data['name'],
        data.get('color_scheme', 'purple')
    )
    job.mode = mode # Store mode
    job.replace_playlist_id = replace_playlist_id
    
    jobs[job_id] = job
    
    # Start processing in background
    thread = Thread(target=process_indexing_job, args=(job,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id, 'status': 'processing'})


@app.route('/api/playlist-preview', methods=['POST'])
def playlist_preview():
    data = request.get_json(silent=True) or {}
    playlist_url = str(data.get("playlist_url") or "").strip()
    if not playlist_url:
        return jsonify({"error": "playlist_url is required"}), 400

    try:
        preview = fetch_playlist_preview(playlist_url)
        requested_name = str(data.get("name") or preview.get("title") or "").strip()
        preview["conflict"] = find_playlist_conflicts(requested_name, playlist_url)
        return jsonify(preview)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/sync/delta/<playlist_id>', methods=['POST'])
def delta_sync_playlist(playlist_id):
    """
    Trigger a delta sync for modification mode.
    Compares existing local data with current YouTube state and applies delta.
    """
    data = request.json
    playlist_url = data.get('playlist_url')
    
    if not playlist_url:
        return jsonify({'error': 'playlist_url required'}), 400
    
    try:
        # Load existing data
        registry = load_playlists_registry()
        playlist_info = next((p for p in registry['playlists'] if p['id'] == playlist_id), None)
        
        if not playlist_info:
            return jsonify({'error': 'Playlist not found in registry'}), 404
            
        data_file = os.path.join(playlist_info['output_dir'], f"{playlist_id}_data.json")
        if get_data_backend() == "json" and not os.path.exists(data_file):
            return jsonify({'error': 'Playlist data file not found'}), 404

        if get_data_backend() == "sqlite":
            existing_videos = get_sqlite_store().load_playlist_videos(playlist_id)
        else:
            existing_videos = read_json_file(data_file, [])
        
        # Fetch current state from YouTube
        from youtube_api_extractor import YouTubeAPIExtractor
        extractor = YouTubeAPIExtractor()
        current_videos = extractor.get_playlist_videos(playlist_url)
        
        # Apply delta sync
        result_videos, stats = delta_sync.apply_delta_with_stats(
            existing_videos, 
            current_videos, 
            keep_removed=True
        )
        
        # Save updated data
        if get_data_backend() == "sqlite":
            get_sqlite_store().save_playlist_videos(playlist_id, playlist_info.get("name", ""), result_videos)
        else:
            write_json_atomic(data_file, result_videos)
        
        # Update registry
        playlist_info['video_count'] = len([v for v in result_videos 
                                            if v.get('sync_status', {}).get('exists_at_source', True)])
        playlist_info['last_updated'] = utc_now_iso()
        
        if get_data_backend() == "sqlite":
            get_sqlite_store().upsert_playlist(playlist_info)
        else:
            write_registry_json(registry)
        
        return jsonify({
            'status': 'success',
            'playlist_id': playlist_id,
            'stats': stats,
            'total_videos': len(result_videos)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500




@app.route('/api/status/<job_id>')
def job_status(job_id):
    """Stream job progress via Server-Sent Events."""
    def generate():
        if job_id not in jobs:
            yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
            return
        
        job = jobs[job_id]
        yield "retry: 1000\n\n"
        
        while job.status not in ['complete', 'error']:
            data = {
                'status': job.status,
                'progress': job.progress,
                'message': job.message,
                'quota_used': job.quota_used
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.5)
        
        # Final update
        if job.status == 'complete':
            data = {
                'status': 'complete',
                'progress': 100,
                'message': 'Indexing complete!',
                'files': job.result,
                'quota_used': job.quota_used
            }
        else:
            data = {
                'status': 'error',
                'message': job.error
            }
        
        yield f"data: {json.dumps(data)}\n\n"

    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, no-transform'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Connection'] = 'keep-alive'
    return response


@app.route('/api/quota')
def get_quota():
    """Get current YouTube API quota information."""
    try:
        api_key = get_youtube_api_key()
        if not api_key:
            return jsonify({'remaining': 0, 'total': 10000, 'percentage': 0})

        # Estimate remaining quota (would need actual Google Cloud API for real data)
        # For now, return static estimate
        return jsonify({
            'remaining': 9847,
            'total': 10000,
            'percentage': 98.47
        })
        
    except Exception as e:
        return jsonify({'remaining': 0, 'total': 10000, 'percentage': 0})


@app.route('/api/search')
def search_playlists():
    """Search across all indexed playlists."""
    query = request.args.get('q', '')
    playlist_filter = request.args.get('playlist', '')
    category_filter = request.args.get('category', '')
    logic = request.args.get('logic', 'or').strip().lower()
    in_description = _to_bool(request.args.get('in_description'), True)
    fields = request.args.get('fields', 'title,channel,tags,description')
    fields = [f.strip().lower() for f in fields.split(',') if f.strip()]
    
    # Load all playlists data
    videos = load_all_videos()
    
    # Apply filters
    videos = filter_video_list(
        videos,
        query,
        playlist_filter,
        category_filter,
        logic=logic,
        fields=fields,
        in_description=in_description
    )
    
    return jsonify({
        'results': videos[:50],  # Limit to 50 results
        'total': len(videos),
        'logic': logic if logic in {'and', 'or'} else 'or',
        'in_description': in_description,
        'fields': fields
    })


def filter_video_list(
    videos: List[Dict[str, Any]],
    query: str,
    playlist_filter: str,
    category_filter: str,
    logic: str = "or",
    fields: Optional[List[str]] = None,
    in_description: bool = True
):
    """
    Filter a list of videos based on search criteria.
    
    Args:
        videos: List of video dictionaries
        query: Text query to search in title/channel/description/tags
        playlist_filter: Filter by specific playlist ID
        category_filter: Filter by category/thematic
        
    Returns:
        List of filtered video dictionaries
    """
    filtered = videos
    fields = fields or ["title", "channel", "tags", "description"]

    if not in_description and "description" in fields:
        fields = [f for f in fields if f != "description"]

    if query:
        query = query.lower().strip()
        raw_tokens = [t for t in re.split(r"\s+", query) if t]
        tokens = [t for t in raw_tokens if re.search(r"[0-9a-zA-Z\u0080-\uffff]", t)]

        def token_in_video(v: Dict[str, Any], token: str) -> bool:
            if "title" in fields and token in v.get("title", "").lower():
                return True
            if "channel" in fields and token in v.get("channel", "").lower():
                return True
            if "description" in fields and token in v.get("description", "").lower():
                return True
            if "tags" in fields and any(token in tag.lower() for tag in _get_video_tags(v)):
                return True
            return False

        use_and = logic == "and"
        if use_and:
            filtered = [
                v for v in filtered
                if all(token_in_video(v, token) for token in tokens)
            ]
        else:
            filtered = [
                v for v in filtered
                if any(token_in_video(v, token) for token in tokens)
            ]
    
    if playlist_filter:
        filtered = [v for v in filtered if v.get('playlist_id') == playlist_filter]
    
    if category_filter:
        filtered = [v for v in filtered if 
                    v.get('category') == category_filter or
                    v.get('metadata', {}).get('thematic', {}).get('primary') == category_filter]
                    
    return filtered


def _get_video_tags(video):
    """Helper to extract tags from video in various formats."""
    tags = video.get('tags', [])
    if isinstance(tags, dict):
        return tags.get('combined', [])
    elif isinstance(tags, list):
        return tags
    return []    


def _slugify_playlist_name(name: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", (name or "").strip().lower())
    text = text.strip("_")
    return text or "playlist"


def build_playlist_record_id(name: str, youtube_url: str) -> str:
    playlist_id = extract_playlist_id_from_url(youtube_url or "")
    if playlist_id:
        return playlist_id
    return _slugify_playlist_name(name)


def normalize_playlist_name(name: str) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", (name or "").strip().lower())
    return " ".join(text.split())


def find_playlist_conflicts(name: str, youtube_url: str, registry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    registry = registry if isinstance(registry, dict) else load_playlists_registry()
    playlists = registry.get("playlists", []) if isinstance(registry, dict) else []
    requested_playlist_id = extract_playlist_id_from_url(youtube_url or "")
    requested_name = normalize_playlist_name(name)

    exact_id_match = None
    name_matches: List[Dict[str, Any]] = []
    seen_name_match_ids = set()

    for playlist in playlists:
        if not isinstance(playlist, dict):
            continue
        existing_id = str(playlist.get("id", "") or "").strip()
        existing_url_id = extract_playlist_id_from_url(playlist.get("youtube_url", "") or "")

        if requested_playlist_id and (existing_url_id == requested_playlist_id or existing_id == requested_playlist_id):
            exact_id_match = playlist

        if requested_name and normalize_playlist_name(playlist.get("name", "")) == requested_name:
            match_id = existing_id or f"name:{playlist.get('name', '')}"
            if match_id not in seen_name_match_ids:
                name_matches.append(playlist)
                seen_name_match_ids.add(match_id)

    recommended_replace_id = None
    reason = None
    if exact_id_match:
        recommended_replace_id = exact_id_match.get("id")
        reason = "playlist_id"
    elif len(name_matches) == 1:
        recommended_replace_id = name_matches[0].get("id")
        reason = "name"
    elif name_matches:
        reason = "name"

    return {
        "has_conflict": bool(exact_id_match or name_matches),
        "reason": reason,
        "requested_playlist_id": requested_playlist_id or None,
        "requested_name": name or "",
        "normalized_name": requested_name,
        "recommended_replace_id": recommended_replace_id,
        "exact_id_match": exact_id_match,
        "name_matches": name_matches,
    }


def _path_within_output_root(path: str) -> bool:
    if not path:
        return False
    output_root = os.path.abspath(os.path.join(get_app_root(), "output"))
    abs_path = os.path.abspath(path)
    try:
        return os.path.commonpath([output_root, abs_path]) == output_root
    except ValueError:
        return False


def _safe_remove_file(path: str):
    if not path or not _path_within_output_root(path):
        return
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def cleanup_playlist_artifacts(playlist: Dict[str, Any]):
    if not isinstance(playlist, dict):
        return
    output_dir = str(playlist.get("output_dir", "") or "")
    playlist_id = str(playlist.get("id", "") or "")
    if output_dir and playlist_id:
        _safe_remove_file(os.path.join(output_dir, f"{playlist_id}_data.json"))



@app.route('/api/playlists')
def list_playlists():
    """Get list of all indexed playlists."""
    registry = load_playlists_registry()
    return jsonify(registry)


@app.route('/api/playlist/<playlist_id>')
def get_playlist(playlist_id):
    """Get a single playlist with all its videos."""
    registry = load_playlists_registry()
    
    # Find playlist by ID
    playlist = next((p for p in registry['playlists'] if p['id'] == playlist_id), None)
    
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404
    
    # Load videos
    videos = load_playlist_videos(playlist)
    
    return jsonify({
        'playlist': playlist,
        'videos': videos
    })

@app.route('/playlist/<playlist_id>')
def view_playlist(playlist_id):
    """Render the main view for a single playlist."""
    # Since we don't have a dedicated playlist.html template yet, let's reuse share.html
    # for the time being, or redirect to share page, but better to render as standard view.
    registry = load_playlists_registry()

    playlist = next((p for p in registry['playlists'] if p['id'] == playlist_id), None)

    if not playlist:
        return "Playlist not found", 404

    videos = load_playlist_videos(playlist)

    # Note: If there's a specific 'playlist.html' in the future, use it here.
    return render_template('share.html', playlist=playlist, videos=videos)


@app.route('/share/<playlist_id>')
def share_playlist(playlist_id):
    """Render a shareable standalone page for a playlist."""
    registry = load_playlists_registry()
    
    # Find playlist by ID
    playlist = next((p for p in registry['playlists'] if p['id'] == playlist_id), None)
    
    if not playlist:
        return "Playlist not found", 404
    
    # Load videos
    videos = load_playlist_videos(playlist)
    
    return render_template('share.html', playlist=playlist, videos=videos)


@app.route('/api/videos/all')
def get_all_videos():
    """Get all videos from all indexed playlists."""
    all_videos = load_all_videos()
    
    # Get unique playlists
    playlists = list(set(v.get('playlist_id', '') for v in all_videos))
    playlists = [p for p in playlists if p]  # Remove empty strings
    
    return jsonify({
        'videos': all_videos,
        'total_count': len(all_videos),
        'playlists': sorted(playlists)
    })


@app.route('/api/export/excel')
def export_excel():
    """Export playlist(s) to Excel file."""
    from io import BytesIO
    from urllib.parse import quote
    from execution.excel_exporter import export_to_excel, load_playlist_videos, load_all_videos as load_all_for_export
    
    filename = "export.xlsx"
    playlist_id = request.args.get('playlist', '')
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    try:
        # Load all videos (easier to just filter from all than selective load for search)
        videos = load_all_for_export()
        
        # Determine filename base
        if playlist_id:
            filename = f"{playlist_id}_filtered_export.xlsx"
        elif query:
            filename = "search_results_export.xlsx"
        else:
            filename = "all_videos_export.xlsx"
            
        # Apply filters
        videos = filter_video_list(videos, query, playlist_id, category)

        
        if not videos:
            return jsonify({'error': 'No videos to export'}), 404
        
        # Create Excel in memory
        output = BytesIO()
        export_to_excel(videos, output)
        output.seek(0)
        excel_data = output.getvalue()
        
        # Create response with proper headers for browser compatibility
        response = Response(
            excel_data,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # RFC 5987 compliant Content-Disposition with both filename and filename*
        # This ensures maximum browser compatibility
        encoded_filename = quote(filename)
        response.headers['Content-Disposition'] = (
            f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
        )
        response.headers['Content-Length'] = len(excel_data)
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/tags')
def list_unique_tags():
    """Get all unique tags across all videos."""
    # This requires loading all video data into Pydantic models ideally
    # For now, we load dicts and pass to TagManager if it accepts dicts or convert
    # TagManager expects List[List[VideoData]]
    all_videos_dicts = load_all_videos()
    # Convert to models (expensive? maybe just adapt TagManager to be flexible later)
    # For now let's assume TagManager can handle dicts or we ignore type hint runtime
    # But better to use helper that extracts tags from dicts
    
    # Extract tags manually to avoid heavy instantiation
    youtube = set()
    auto = set()
    user = set()
    for v in all_videos_dicts:
        tags = v.get('tags', {})
        if isinstance(tags, dict):
             youtube.update(tags.get('youtube_tags', []))
             auto.update(tags.get('auto_generated', []))
             user.update(tags.get('user_defined', []))
        elif isinstance(tags, list):
             youtube.update(tags)
             
    return jsonify({
        "youtube_tags": sorted(list(youtube)),
        "auto_generated": sorted(list(auto)),
        "user_defined": sorted(list(user)),
        "all": sorted(list(youtube | auto | user))
    })


def find_video_across_playlists(video_id: str):
    """Return tuple (playlist_dict, videos_list, target_video) or (None, None, None)."""
    if get_data_backend() == "sqlite":
        found = get_sqlite_store().find_video(video_id)
        if not found:
            return None, None, None
        playlist_id, video = found
        playlist = get_sqlite_store().get_playlist(playlist_id) or {"id": playlist_id, "name": video.get("playlist_name", "")}
        videos = get_sqlite_store().load_playlist_videos(playlist_id)
        target_video = next((v for v in videos if v.get("video_id") == video_id), None)
        if not target_video:
            target_video = video
            videos.append(target_video)
        return playlist, videos, target_video

    registry = load_playlists_registry()
    for p in registry.get("playlists", []):
        videos = load_playlist_videos(p)
        for v in videos:
            if v.get("video_id") == video_id:
                return p, videos, v
    return None, None, None


def persist_updated_video(playlist: Dict[str, Any], videos: List[Dict[str, Any]], updated_video: Dict[str, Any]):
    """Persist an updated video in the active backend."""
    if get_data_backend() == "sqlite":
        playlist_id = playlist.get("id", "")
        if playlist_id:
            get_sqlite_store().update_video(playlist_id, updated_video)
            return
    save_playlist_videos(playlist, videos)

@app.route('/api/videos/<video_id>/tags', methods=['POST'])
def add_user_tag(video_id):
    """Add a user tag to a video."""
    data = request.json
    tag = data.get('tag')
    if not tag:
        return jsonify({'error': 'No tag provided'}), 400
        
    # We need to find the playlist this video belongs to, load it, update it, save it
    # This logic is complex because videos are spread across files
    # Shortcut: search in all loading (slow) or use an index?
    # For prototype: Load all playlists, find video, update specific file
    
    target_playlist, videos, target_video = find_video_across_playlists(video_id)
            
    if not target_video:
        return jsonify({'error': 'Video not found'}), 404
        
    # Update Tag
    tags = target_video.get('tags')
    if isinstance(tags, list):
        # Migrate on fly?
        tags = {'youtube_tags': tags, 'user_defined': [], 'auto_generated': [], 'combined': tags}
        target_video['tags'] = tags
        
    if 'user_defined' not in tags: tags['user_defined'] = []
    if tag not in tags['user_defined']:
        tags['user_defined'].append(tag)
        # Update combined
        # Re-calc combined
        combined = set(tags.get('youtube_tags', []) + tags.get('auto_generated', []) + tags['user_defined'])
        tags['combined'] = list(combined)
        
    # Save back to storage
    save_playlist_videos(target_playlist, videos)
        
    return jsonify({'status': 'success', 'video': target_video})

@app.route('/api/videos/<video_id>/tags/<tag_name>', methods=['DELETE'])
def remove_user_tag(video_id, tag_name):
    """Remove a user-defined tag from a video."""
    # Find the video across all playlists
    target_playlist, videos, target_video = find_video_across_playlists(video_id)
            
    if not target_video:
        return jsonify({'error': 'Video not found'}), 404
        
    # Get tags structure
    tags = target_video.get('tags')
    if isinstance(tags, list):
        # Legacy format - cannot remove from flat list
        return jsonify({'error': 'Cannot remove tags from legacy format'}), 400
        
    if not isinstance(tags, dict) or 'user_defined' not in tags:
        return jsonify({'error': 'No user-defined tags found'}), 404
        
    # Remove the tag if it exists
    if tag_name not in tags['user_defined']:
        return jsonify({'error': 'Tag not found in user-defined tags'}), 404
        
    tags['user_defined'].remove(tag_name)
    
    # Recalculate combined tags
    combined = set(tags.get('youtube_tags', []) + tags.get('auto_generated', []) + tags['user_defined'])
    tags['combined'] = list(combined)
    
    # Save back to storage
    save_playlist_videos(target_playlist, videos)
        
    return jsonify({'status': 'success', 'video': target_video})


@app.route('/api/videos/<video_id>/notes', methods=['POST'])
def set_video_notes(video_id):
    """Set notes for a video and persist to backend storage."""
    data = request.json or {}
    notes = str(data.get("notes", "") or "")

    target_playlist, videos, target_video = find_video_across_playlists(video_id)
    if not target_video:
        return jsonify({"error": "Video not found"}), 404

    target_video["notes"] = notes
    save_playlist_videos(target_playlist, videos)
    return jsonify({"status": "success", "video_id": video_id, "notes": notes})


@app.route('/api/playlists/<playlist_id>/folder', methods=['POST'])
def set_playlist_folder(playlist_id):
    """Assign folder/category to playlist."""
    data = request.json or {}
    folder = data.get("folder")
    if folder is not None:
        folder = str(folder).strip()
        if folder == "":
            folder = None

    if get_data_backend() == "sqlite":
        updated = get_sqlite_store().set_playlist_folder(playlist_id, folder)
        if not updated:
            return jsonify({"error": "Playlist not found"}), 404
        return jsonify({"status": "success", "playlist_id": playlist_id, "folder": folder})

    registry = load_playlists_registry()
    target = next((p for p in registry.get("playlists", []) if p.get("id") == playlist_id), None)
    if not target:
        return jsonify({"error": "Playlist not found"}), 404

    target["folder"] = folder
    registry["total_playlists"] = len(registry.get("playlists", []))
    registry["total_videos"] = sum(int(p.get("video_count", 0) or 0) for p in registry.get("playlists", []))
    registry["last_updated"] = utc_now_iso(z_suffix=True)
    write_registry_json(registry)
    return jsonify({"status": "success", "playlist_id": playlist_id, "folder": folder})


@app.route('/api/folders')
def list_folders():
    """List playlist folders with counts."""
    if get_data_backend() == "sqlite":
        return jsonify({"folders": get_sqlite_store().list_folders()})

    registry = load_playlists_registry()
    counts: Dict[str, int] = {}
    for p in registry.get("playlists", []):
        name = (p.get("folder") or "").strip()
        if not name:
            continue
        counts[name] = counts.get(name, 0) + 1

    folders = [{"name": k, "count": counts[k]} for k in sorted(counts.keys())]
    return jsonify({"folders": folders})


def _assistant_fallback_answer(message: str, videos: List[Dict[str, Any]]) -> str:
    msg = (message or "").strip().lower()
    total = len(videos)
    if total == 0:
        return "No indexed videos matched your current context."

    channels: Dict[str, int] = {}
    tags: Dict[str, int] = {}
    for v in videos:
        ch = (v.get("channel") or "Unknown").strip()
        channels[ch] = channels.get(ch, 0) + 1
        for t in _get_video_tags(v):
            t_norm = t.strip()
            if not t_norm:
                continue
            tags[t_norm] = tags.get(t_norm, 0) + 1

    top_channels = sorted(channels.items(), key=lambda x: x[1], reverse=True)[:3]
    top_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:5]

    if "beginner" in msg:
        beginner_hits = [v for v in videos if "beginner" in (v.get("title", "") + " " + v.get("description", "")).lower()]
        if beginner_hits:
            picks = "\n".join(f"- {v.get('title', 'Untitled')}" for v in beginner_hits[:5])
            return f"I found {len(beginner_hits)} beginner-oriented videos:\n{picks}"
        return "I did not find explicit 'beginner' matches in the current context."

    if "overlap" in msg or "common" in msg:
        if not top_tags:
            return "I couldn't detect strong shared tags in this context."
        tags_line = ", ".join(f"{k} ({n})" for k, n in top_tags[:5])
        return f"Common overlapping topics are: {tags_line}."

    if "summarize" in msg or "summary" in msg:
        ch_line = ", ".join(f"{k} ({n})" for k, n in top_channels) if top_channels else "no channel distribution available"
        tg_line = ", ".join(f"{k} ({n})" for k, n in top_tags) if top_tags else "no dominant tags"
        return (
            f"Summary: {total} videos in scope. "
            f"Top channels: {ch_line}. "
            f"Dominant tags/topics: {tg_line}."
        )

    return (
        f"I analyzed {total} videos in scope. "
        f"Top channels: {', '.join(f'{k} ({n})' for k, n in top_channels) if top_channels else 'N/A'}. "
        f"Top tags: {', '.join(f'{k} ({n})' for k, n in top_tags) if top_tags else 'N/A'}."
    )


@app.route('/api/assistant/chat', methods=['POST'])
def assistant_chat():
    """Stage-B assistant endpoint with safe fallback behavior."""
    data = request.json or {}
    message = str(data.get("message", "") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    scope = data.get("scope", {}) if isinstance(data.get("scope", {}), dict) else {}
    playlist_id = str(scope.get("playlist_id", "") or "").strip()
    query = str(scope.get("query", "") or "").strip()
    try:
        limit = int(scope.get("limit", 50))
    except (TypeError, ValueError):
        limit = 50
    limit = max(1, min(limit, 200))

    if playlist_id:
        registry = load_playlists_registry()
        playlist = next((p for p in registry.get("playlists", []) if p.get("id") == playlist_id), None)
        videos = load_playlist_videos(playlist) if playlist else []
    else:
        videos = load_all_videos()

    if query:
        videos = filter_video_list(videos, query, "", "", logic="or", fields=["title", "channel", "description", "tags"], in_description=True)
    videos = videos[:limit]

    answer = _assistant_fallback_answer(message, videos)
    return jsonify({
        "answer": answer,
        "sources": len(videos),
        "mode": "fallback"
    })


def _assistant_scope_videos(scope: Dict[str, Any]) -> List[Dict[str, Any]]:
    playlist_id = str(scope.get("playlist_id", "") or "").strip()
    query = str(scope.get("query", "") or "").strip()
    try:
        limit = int(scope.get("limit", 80))
    except (TypeError, ValueError):
        limit = 80
    limit = max(1, min(limit, 300))

    if playlist_id:
        registry = load_playlists_registry()
        playlist = next((p for p in registry.get("playlists", []) if p.get("id") == playlist_id), None)
        videos = load_playlist_videos(playlist) if playlist else []
    else:
        videos = load_all_videos()

    if query:
        videos = filter_video_list(
            videos,
            query,
            "",
            "",
            logic="or",
            fields=["title", "channel", "description", "tags"],
            in_description=True,
        )
    return videos[:limit]


def _build_llm_context(videos: List[Dict[str, Any]], max_items: int = 120) -> str:
    selected = videos[:max_items]
    lines = []
    for idx, v in enumerate(selected, 1):
        tags = _get_video_tags(v)[:8]
        lines.append(
            f"{idx}. title={v.get('title','')}; "
            f"channel={v.get('channel','')}; "
            f"playlist={v.get('playlist_name','')}; "
            f"tags={','.join(tags)}; "
            f"description={(v.get('description','') or '')[:180]}"
        )
    header = f"Context videos: {len(videos)} total, {len(selected)} included below.\n"
    context = header + "\n".join(lines)
    return context[:18000]


def _normalized_history(history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for item in history:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "")).strip().lower()
        if role not in {"user", "assistant"}:
            continue
        content = str(item.get("content", "") or "").strip()
        if content:
            out.append({"role": role, "content": content})
    return out


def _call_openai_chat(
    api_key: str,
    model: str,
    system_prompt: str,
    history: List[Dict[str, Any]],
    user_message: str,
    timeout_seconds: int = 40,
) -> str:
    """Call OpenAI chat completions using user-provided API key."""
    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages.extend(_normalized_history(history))
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    return str(data["choices"][0]["message"]["content"]).strip()


def _call_openrouter_chat(
    api_key: str,
    model: str,
    system_prompt: str,
    history: List[Dict[str, Any]],
    user_message: str,
    timeout_seconds: int = 40,
) -> str:
    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages.extend(_normalized_history(history))
    messages.append({"role": "user", "content": user_message})
    payload = {"model": model, "messages": messages, "temperature": 0.2}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Playlist Navigator Pro",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    return str(data["choices"][0]["message"]["content"]).strip()


def _call_anthropic_chat(
    api_key: str,
    model: str,
    system_prompt: str,
    history: List[Dict[str, Any]],
    user_message: str,
    timeout_seconds: int = 40,
) -> str:
    messages = _normalized_history(history)
    messages.append({"role": "user", "content": user_message})
    payload = {
        "model": model,
        "max_tokens": 1024,
        "temperature": 0.2,
        "system": system_prompt,
        "messages": messages,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    parts = data.get("content", [])
    text_parts = [str(p.get("text", "")).strip() for p in parts if isinstance(p, dict) and p.get("type") == "text"]
    return "\n".join([p for p in text_parts if p]).strip()


def _call_gemini_chat(
    api_key: str,
    model: str,
    system_prompt: str,
    history: List[Dict[str, Any]],
    user_message: str,
    timeout_seconds: int = 40,
) -> str:
    contents = []
    for item in _normalized_history(history):
        role = "model" if item["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": item["content"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.2},
    }
    body = json.dumps(payload).encode("utf-8")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    candidates = data.get("candidates", [])
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [str(p.get("text", "")).strip() for p in parts if isinstance(p, dict)]
    return "\n".join([p for p in text_parts if p]).strip()


def _call_provider_chat(
    provider: str,
    api_key: str,
    model: str,
    system_prompt: str,
    history: List[Dict[str, Any]],
    user_message: str,
) -> str:
    provider = (provider or "").strip().lower()
    if provider == "openai":
        return _call_openai_chat(api_key, model, system_prompt, history, user_message)
    if provider == "openrouter":
        return _call_openrouter_chat(api_key, model, system_prompt, history, user_message)
    if provider == "anthropic":
        return _call_anthropic_chat(api_key, model, system_prompt, history, user_message)
    if provider == "gemini":
        return _call_gemini_chat(api_key, model, system_prompt, history, user_message)
    raise ValueError("Unsupported provider. Use: openai, openrouter, anthropic, gemini.")


@app.route('/api/assistant/llm-chat', methods=['POST'])
def assistant_llm_chat():
    """
    Assistant endpoint with optional external LLM call.
    If api_key is missing or LLM call fails, falls back to local deterministic assistant.
    """
    data = request.json or {}
    message = str(data.get("message", "") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    scope = data.get("scope", {}) if isinstance(data.get("scope", {}), dict) else {}
    videos = _assistant_scope_videos(scope)
    fallback = _assistant_fallback_answer(message, videos)
    session_id = str(data.get("session_id", "") or "default").strip() or "default"

    runtime_defaults = get_assistant_runtime_defaults()
    provider = str(data.get("provider", "") or runtime_defaults.get("provider", "gemini")).strip().lower()
    model_default = {
        "openai": "gpt-4o-mini",
        "openrouter": "openai/gpt-4o-mini",
        "anthropic": "claude-3-5-sonnet-latest",
        "gemini": "gemini-3-flash-preview",
    }.get(provider, "gpt-4o-mini")
    model = str(data.get("model", "") or "").strip() or str(runtime_defaults.get("model", "") or "").strip() or model_default
    api_key = str(data.get("api_key", "") or "").strip() or str(runtime_defaults.get("api_key", "") or "").strip()
    incoming_history = data.get("history", [])
    if not isinstance(incoming_history, list):
        incoming_history = []
    stored_history = get_assistant_history(session_id)
    history = (stored_history + incoming_history)[-30:]
    memory_store = load_assistant_memory_store()
    memory_items = memory_store.get("memory", {}).get("items", [])
    if not isinstance(memory_items, list):
        memory_items = []
    memory_blob = "\n".join(f"- {m}" for m in memory_items[-30:])
    memory_blob = memory_blob[:4000]

    append_assistant_history(session_id, "user", message)

    if not api_key:
        append_assistant_history(session_id, "assistant", fallback)
        return jsonify({
            "mode": "fallback",
            "provider": "local",
            "model": "fallback",
            "answer": fallback,
            "sources": len(videos),
            "session_id": session_id,
            "history": get_assistant_history(session_id),
            "memory": load_assistant_memory_store().get("memory", {}),
        })

    context_blob = _build_llm_context(videos)
    system_prompt = (
        "You are Playlist Navigator Assistant. "
        "Use provided playlist/video context first, be concise, and avoid hallucinations. "
        "If context is insufficient, say so.\n\n"
        f"User memory:\n{memory_blob if memory_blob else '- (empty)'}\n\n"
        f"{context_blob}"
    )
    try:
        answer = _call_provider_chat(provider, api_key, model, system_prompt, history, message)
        if not answer:
            answer = fallback
            mode = "fallback"
        else:
            mode = "llm"
    except Exception as exc:
        answer = fallback
        mode = "fallback"
        append_assistant_history(session_id, "assistant", answer)
        return jsonify({
            "mode": mode,
            "provider": provider,
            "model": model,
            "answer": answer,
            "sources": len(videos),
            "session_id": session_id,
            "history": get_assistant_history(session_id),
            "memory": load_assistant_memory_store().get("memory", {}),
            "warning": f"LLM call failed; fallback used ({str(exc)})",
        })

    append_assistant_history(session_id, "assistant", answer)
    return jsonify({
        "mode": mode,
        "provider": provider,
        "model": model,
        "answer": answer,
        "sources": len(videos),
        "session_id": session_id,
        "history": get_assistant_history(session_id),
        "memory": load_assistant_memory_store().get("memory", {}),
    })


@app.route('/api/assistant/history')
def assistant_history():
    session_id = str(request.args.get("session_id", "") or "default").strip() or "default"
    store = load_assistant_memory_store()
    history = store.get("conversations", {}).get(session_id, [])
    if not isinstance(history, list):
        history = []
    return jsonify({
        "session_id": session_id,
        "history": history,
        "memory": store.get("memory", {"items": [], "updated_at": None}),
    })


@app.route('/api/assistant/history', methods=['DELETE'])
def assistant_history_clear():
    session_id = str(request.args.get("session_id", "") or "default").strip() or "default"
    clear_memory = _to_bool(request.args.get("clear_memory"), False)
    store = load_assistant_memory_store()
    if session_id == "*":
        store["conversations"] = {}
    else:
        store.get("conversations", {}).pop(session_id, None)
    if clear_memory:
        store["memory"] = {"items": [], "updated_at": utc_now_iso(z_suffix=True)}
    save_assistant_memory_store(store)
    return jsonify({"status": "success", "session_id": session_id, "clear_memory": clear_memory})


def build_analytics_summary_json(videos: List[Dict[str, Any]], playlists: List[Dict[str, Any]]) -> Dict[str, Any]:
    channels: Dict[str, int] = {}
    categories: Dict[str, int] = {}
    progress: Dict[str, int] = {}
    watch_seconds = 0

    for v in videos:
        ch = (v.get("channel") or "Unknown").strip() or "Unknown"
        channels[ch] = channels.get(ch, 0) + 1
        cat = v.get("metadata", {}).get("thematic", {}).get("primary") or "unknown"
        categories[cat] = categories.get(cat, 0) + 1
        state = v.get("progress_status") or "not_started"
        progress[state] = progress.get(state, 0) + 1
        watch_seconds += int(v.get("duration_seconds", 0) or 0)

    top_channels = sorted(channels.items(), key=lambda x: x[1], reverse=True)[:10]
    category_list = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    return {
        "total_playlists": len(playlists),
        "total_videos": len(videos),
        "total_watch_time_seconds": watch_seconds,
        "top_channels": [{"channel": c, "count": n} for c, n in top_channels],
        "categories": [{"category": c, "count": n} for c, n in category_list],
        "progress": progress,
    }


@app.route('/api/analytics/summary')
def analytics_summary():
    """Stage-D analytics summary endpoint."""
    if get_data_backend() == "sqlite":
        return jsonify(get_sqlite_store().analytics_summary())

    registry = load_playlists_registry()
    videos = load_all_videos()
    return jsonify(build_analytics_summary_json(videos, registry.get("playlists", [])))


def run_auto_sync_once(dry_run: bool = False) -> Dict[str, Any]:
    """Run one sync cycle across known playlists."""
    registry = load_playlists_registry()
    playlists = registry.get("playlists", [])
    checked = 0
    skipped = 0
    synced = 0
    errors: List[Dict[str, Any]] = []

    for p in playlists:
        checked += 1
        playlist_id = p.get("id", "")
        playlist_url = p.get("youtube_url", "")
        if not playlist_id or not playlist_url:
            skipped += 1
            continue

        if dry_run:
            synced += 1
            continue

        try:
            from youtube_api_extractor import YouTubeAPIExtractor
            extractor = YouTubeAPIExtractor()
            existing_videos = load_playlist_videos(p)
            current_videos = extractor.get_playlist_videos(playlist_url)
            result_videos, _ = delta_sync.apply_delta_with_stats(existing_videos, current_videos, keep_removed=True)
            save_playlist_videos(p, result_videos)
            p["video_count"] = len([v for v in result_videos if v.get("sync_status", {}).get("exists_at_source", True)])
            p["last_updated"] = utc_now_iso(z_suffix=True)
            if get_data_backend() == "sqlite":
                get_sqlite_store().upsert_playlist(p)
            synced += 1
        except Exception as exc:
            errors.append({"playlist_id": playlist_id, "error": str(exc)})

    if (not dry_run) and get_data_backend() != "sqlite":
        write_registry_json(registry)

    result = {
        "status": "success",
        "dry_run": bool(dry_run),
        "playlists_checked": checked,
        "playlists_synced": synced,
        "playlists_skipped": skipped,
        "errors": errors,
    }
    sync_scheduler.last_run_at = utc_now_iso(z_suffix=True)
    sync_scheduler.last_result = result
    return result


@app.route('/api/scheduler/status')
def scheduler_status():
    return jsonify(sync_scheduler.status())


@app.route('/api/scheduler/config', methods=['POST'])
def scheduler_config():
    data = request.json or {}
    enabled = bool(data.get("enabled", False))
    try:
        interval = int(data.get("interval_minutes", 60))
    except (TypeError, ValueError):
        interval = 60
    interval = max(5, min(interval, 1440))

    cfg = load_runtime_config()
    auto_sync_cfg = cfg.get("auto_sync") if isinstance(cfg.get("auto_sync"), dict) else {}
    auto_sync_cfg["enabled"] = enabled
    auto_sync_cfg["interval_minutes"] = interval
    cfg["auto_sync"] = auto_sync_cfg
    save_runtime_config(cfg)

    sync_scheduler.configure(enabled, interval)
    return jsonify(sync_scheduler.status())


@app.route('/api/scheduler/run-once', methods=['POST'])
def scheduler_run_once():
    data = request.json or {}
    return jsonify(run_auto_sync_once(dry_run=bool(data.get("dry_run", False))))


def _video_summary_text(video: Dict[str, Any]) -> str:
    title = (video.get("title") or "Untitled").strip()
    channel = (video.get("channel") or "Unknown channel").strip()
    thematic = video.get("metadata", {}).get("thematic", {}).get("primary") or "unknown"
    difficulty = video.get("metadata", {}).get("difficulty_level") or "intermediate"
    desc = (video.get("description") or "").strip()
    short_desc = desc[:200] + ("..." if len(desc) > 200 else "")
    return (
        f"{title} by {channel}. "
        f"Theme: {thematic}. Difficulty: {difficulty}. "
        f"Summary: {short_desc or 'No description provided.'}"
    )


def _recommend_videos(video_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    all_items = load_all_videos()
    base = next((v for v in all_items if v.get("video_id") == video_id), None)
    if not base:
        return []

    base_tags = set(_get_video_tags(base))
    base_theme = base.get("metadata", {}).get("thematic", {}).get("primary")
    candidates = []
    for v in all_items:
        if v.get("video_id") == video_id:
            continue
        overlap = len(base_tags & set(_get_video_tags(v)))
        theme_match = 1 if base_theme and v.get("metadata", {}).get("thematic", {}).get("primary") == base_theme else 0
        score = overlap * 2 + theme_match
        if score > 0:
            candidates.append((score, v))
    candidates.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "video_id": v.get("video_id"),
            "title": v.get("title"),
            "channel": v.get("channel"),
            "score": score,
        }
        for score, v in candidates[:limit]
    ]


@app.route('/api/ai/summary/<video_id>')
def ai_summary(video_id):
    playlist, videos, target_video = find_video_across_playlists(video_id)
    if not target_video:
        return jsonify({"error": "Video not found"}), 404

    cached = bool(target_video.get("ai_summary"))
    if not cached:
        target_video["ai_summary"] = _video_summary_text(target_video)
        persist_updated_video(playlist, videos, target_video)
    return jsonify({"video_id": video_id, "ai_summary": target_video.get("ai_summary", ""), "cached": cached})


@app.route('/api/ai/suggest-tags/<video_id>')
def ai_suggest_tags(video_id):
    _, _, target_video = find_video_across_playlists(video_id)
    if not target_video:
        return jsonify({"error": "Video not found"}), 404
    return jsonify({"video_id": video_id, "suggested_tags": enricher.generate_auto_tags(target_video)})


@app.route('/api/ai/recommendations/<video_id>')
def ai_recommendations(video_id):
    try:
        limit = int(request.args.get("limit", "5"))
    except (TypeError, ValueError):
        limit = 5
    limit = max(1, min(limit, 20))
    return jsonify({"video_id": video_id, "recommendations": _recommend_videos(video_id, limit=limit)})


@app.route('/api/ai/difficulty-path')
def ai_difficulty_path():
    playlist_id = str(request.args.get("playlist_id", "") or "").strip()
    registry = load_playlists_registry()
    playlist = next((p for p in registry.get("playlists", []) if p.get("id") == playlist_id), None) if playlist_id else None
    videos = load_playlist_videos(playlist) if playlist else load_all_videos()

    levels = {"beginner": [], "intermediate": [], "advanced": []}
    for v in videos:
        level = str(v.get("metadata", {}).get("difficulty_level", "intermediate")).strip().lower()
        if level not in levels:
            level = "intermediate"
        levels[level].append({"video_id": v.get("video_id"), "title": v.get("title", "Untitled")})
    return jsonify({"playlist_id": playlist_id or None, "path": levels})




def load_playlists_registry():
    if get_data_backend() == "sqlite":
        return get_sqlite_store().load_registry()

    registry_file = get_registry_path()
    return read_json_file(registry_file, {'playlists': [], 'total_playlists': 0, 'total_videos': 0})

# Mind Map Route (Moved down)
@app.route('/api/graph/mindmap')
def get_mindmap_data():
    """Get graph data for mind map visualization."""
    from execution.graph_generator import build_graph_data
    from execution.excel_exporter import load_all_videos as load_all_for_graph
    
    try:
        videos = load_all_for_graph()
        # Phase 2: use view mode if passed
        view_mode = request.args.get('view', 'default')
        graph_data = build_graph_data(videos) # Update build_graph_data signature later
        return jsonify(graph_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def process_indexing_job(job):
    """Background job processor."""
    try:
        job.status = "extracting"
        job.progress = 10
        job.message = "Extracting playlist data from YouTube..."
        
        # Initialize indexer
        # Initialize indexer
        indexer = PlaylistIndexer(config_file=get_config_path())
        indexer.config['color_scheme'] = job.color_scheme
        
        if hasattr(job, 'mode') and job.mode == 'overwrite':
            # Handling overwrite specific logic if needed
            pass

        # Extract data
        raw_playlist_data = indexer.extract_from_youtube_url(job.playlist_url)
        job.progress = 40
        
        # Enrich Data (Phase 1 Integration)
        job.message = "Enriching metadata..."
        playlist_data = enricher.process_videos(raw_playlist_data)
        
        job.progress = 60
        job.message = f"Extracted & Enriched {len(playlist_data)} videos"
        
        # Estimate quota
        job.quota_used = len(playlist_data) + 2
        
        job.status = "generating"
        job.progress = 80
        job.message = "Generating index files..."
        
        # Generate files
        output_dir, files = indexer.generate_files(job.name, playlist_data)
        
        # Register playlist
        register_playlist(
            job.name,
            output_dir,
            files,
            playlist_data,
            job.color_scheme,
            job.playlist_url,
            replace_playlist_id=getattr(job, "replace_playlist_id", None),
        )
        
        job.status = "complete"
        job.progress = 100
        job.message = "Complete!"
        job.result = files
        
    except Exception as e:
        job.status = "error"
        job.error = str(e)
        import traceback
        traceback.print_exc()


def register_playlist(name, output_dir, files, playlist_data, color_scheme, youtube_url, replace_playlist_id: Optional[str] = None):
    """Register a newly indexed playlist."""
    registry = load_playlists_registry()
    
    # Prefer stable YouTube playlist IDs over display names.
    safe_id = build_playlist_record_id(name, youtube_url)
    playlists = registry.setdefault("playlists", [])
    replace_target = next((p for p in playlists if p.get("id") == replace_playlist_id), None) if replace_playlist_id else None

    if replace_target and replace_target.get("id") != safe_id:
        if get_data_backend() == "sqlite":
            get_sqlite_store().delete_playlist(replace_target.get("id", ""))
        else:
            cleanup_playlist_artifacts(replace_target)
        registry["playlists"] = [p for p in playlists if p.get("id") != replace_target.get("id")]
        playlists = registry["playlists"]

    existing_idx = next((i for i, p in enumerate(playlists) if p.get('id') == safe_id), None)
    existing = playlists[existing_idx] if existing_idx is not None else None
    preserved = existing or replace_target or {}
    
    playlist_info = {
        'id': safe_id,
        'name': name,
        'created_at': utc_now_iso(z_suffix=True),
        'last_updated': utc_now_iso(z_suffix=True),
        'video_count': len(playlist_data),
        'output_dir': output_dir,
        'html_file': next((f for f in files if f.endswith('.html')), ''),
        'md_file': next((f for f in files if f.endswith('.md')), ''),
        'color_scheme': color_scheme,
        'youtube_url': youtube_url,
        'folder': preserved.get("folder") if isinstance(preserved, dict) else None
    }
    
    if existing_idx is not None:
        playlists[existing_idx] = playlist_info
    else:
        playlists.append(playlist_info)

    # Update totals
    registry['total_playlists'] = len(playlists)
    registry['total_videos'] = sum(int(p.get('video_count', 0) or 0) for p in playlists)
    registry['last_updated'] = utc_now_iso(z_suffix=True)
    
    # Save registry
    base_dir = get_app_root()
    output_root = os.path.join(base_dir, 'output')
    os.makedirs(output_root, exist_ok=True)
    
    # Ensure specific playlist output dir is absolute or relative to base
    # If output_dir coming from indexer is relative 'output/name', we need to make it absolute for safety
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(base_dir, output_dir)
        
    if get_data_backend() == "sqlite":
        get_sqlite_store().upsert_playlist(playlist_info)
    else:
        registry_file = os.path.join(output_root, 'playlists.json')
        write_json_atomic(registry_file, registry)
    
    # Save video data for searching
    data_file = os.path.join(output_dir, f"{safe_id}_data.json")
    video_data_with_playlist = []
    for video in playlist_data:
        video_copy = video.copy()
        video_copy['playlist_id'] = safe_id
        video_copy['playlist_name'] = name
        video_data_with_playlist.append(video_copy)
    
    if get_data_backend() == "sqlite":
        get_sqlite_store().save_playlist_videos(safe_id, name, video_data_with_playlist)
    else:
        write_json_atomic(data_file, video_data_with_playlist)


def load_all_videos():
    """Load all videos from all indexed playlists."""
    if get_data_backend() == "sqlite":
        return get_sqlite_store().load_all_videos()

    all_videos: List[Dict[str, Any]] = []
    registry = load_playlists_registry()

    for playlist in registry.get("playlists", []):
        videos = load_playlist_videos_json(playlist)
        if videos:
            all_videos.extend(videos)

    return all_videos


@app.route('/api/store/categories')
def store_categories():
    """Get thematic categories with counts."""
    return jsonify(store_api.get_categories())

@app.route('/api/store/filters')
def store_filters():
    """Get available filter options."""
    return jsonify(store_api.get_filter_options())

@app.route('/api/store/search')
def store_search():
    """Advanced search for Video Store."""
    try:
        results = store_api.search_videos(
            query=request.args.get('q'),
            thematic=request.args.get('thematic'),
            genre=request.args.get('genre'),
            length=request.args.get('length'),
            author_type=request.args.get('author_type'),
            sort_by=request.args.get('sort', 'newest'),
            page=int(request.args.get('page', 1)),
            per_page=int(request.args.get('per_page', 24))
        )
        return jsonify(results)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def open_browser():
    """Open browser after a short delay to allow server to start."""
    import webbrowser
    time.sleep(1.5) # Wait for server to spin up
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("Starting Playlist Navigator Pro...")
    print("Open your browser to: http://localhost:5000")
    
    # Launch browser in a separate thread
    if not os.environ.get("WERKZEUG_RUN_MAIN"): # Prevent double open with reloader
        Thread(target=open_browser).start()
        
    app.run(debug=True, port=5000, threaded=True)

