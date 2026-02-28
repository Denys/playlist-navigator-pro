import json
import os
import sqlite3
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple


class SQLiteStore:
    """SQLite-backed storage for playlists and videos."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._init_schema()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self._connect() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode=WAL;

                CREATE TABLE IF NOT EXISTS playlists (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT,
                    video_count INTEGER DEFAULT 0,
                    output_dir TEXT,
                    html_file TEXT,
                    md_file TEXT,
                    color_scheme TEXT,
                    youtube_url TEXT,
                    folder TEXT,
                    last_updated TEXT
                );

                CREATE TABLE IF NOT EXISTS videos (
                    video_id TEXT NOT NULL,
                    playlist_id TEXT NOT NULL,
                    playlist_name TEXT,
                    title TEXT,
                    channel TEXT,
                    description TEXT,
                    url TEXT,
                    published_at TEXT,
                    duration_seconds INTEGER DEFAULT 0,
                    notes TEXT,
                    progress_status TEXT,
                    ai_summary TEXT,
                    tags_json TEXT,
                    metadata_json TEXT,
                    data_json TEXT NOT NULL,
                    PRIMARY KEY (video_id, playlist_id),
                    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_videos_title ON videos(title);
                CREATE INDEX IF NOT EXISTS idx_videos_channel ON videos(channel);
                CREATE INDEX IF NOT EXISTS idx_videos_playlist ON videos(playlist_id);
                CREATE INDEX IF NOT EXISTS idx_videos_published_at ON videos(published_at);
                """
            )

    def clear_all(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM videos")
            conn.execute("DELETE FROM playlists")

    def upsert_playlist(self, playlist: Dict[str, Any]):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO playlists (
                    id, name, created_at, video_count, output_dir,
                    html_file, md_file, color_scheme, youtube_url, folder, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    created_at=excluded.created_at,
                    video_count=excluded.video_count,
                    output_dir=excluded.output_dir,
                    html_file=excluded.html_file,
                    md_file=excluded.md_file,
                    color_scheme=excluded.color_scheme,
                    youtube_url=excluded.youtube_url,
                    folder=excluded.folder,
                    last_updated=excluded.last_updated
                """,
                (
                    playlist.get("id"),
                    playlist.get("name"),
                    playlist.get("created_at"),
                    int(playlist.get("video_count", 0)),
                    playlist.get("output_dir"),
                    playlist.get("html_file"),
                    playlist.get("md_file"),
                    playlist.get("color_scheme"),
                    playlist.get("youtube_url"),
                    playlist.get("folder"),
                    playlist.get("last_updated"),
                ),
            )

    def list_playlists(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, name, created_at, video_count, output_dir, html_file,
                       md_file, color_scheme, youtube_url, folder, last_updated
                FROM playlists
                ORDER BY created_at DESC
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def get_playlist(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, name, created_at, video_count, output_dir, html_file,
                       md_file, color_scheme, youtube_url, folder, last_updated
                FROM playlists
                WHERE id=?
                """,
                (playlist_id,),
            ).fetchone()
            return dict(row) if row else None

    def load_registry(self) -> Dict[str, Any]:
        playlists = self.list_playlists()
        return {
            "playlists": playlists,
            "total_playlists": len(playlists),
            "total_videos": sum(int(p.get("video_count", 0) or 0) for p in playlists),
        }

    def save_playlist_videos(self, playlist_id: str, playlist_name: str, videos: List[Dict[str, Any]]):
        with self._connect() as conn:
            conn.execute("DELETE FROM videos WHERE playlist_id=?", (playlist_id,))

            for v in videos:
                tags = v.get("tags", {})
                metadata = v.get("metadata", {})
                conn.execute(
                    """
                    INSERT OR REPLACE INTO videos (
                        video_id, playlist_id, playlist_name, title, channel, description, url,
                        published_at, duration_seconds, notes, progress_status, ai_summary,
                        tags_json, metadata_json, data_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        v.get("video_id"),
                        playlist_id,
                        playlist_name,
                        v.get("title"),
                        v.get("channel"),
                        v.get("description"),
                        v.get("url"),
                        v.get("published_at"),
                        int(v.get("duration_seconds", 0) or 0),
                        v.get("notes"),
                        v.get("progress_status"),
                        v.get("ai_summary"),
                        json.dumps(tags, ensure_ascii=False),
                        json.dumps(metadata, ensure_ascii=False),
                        json.dumps(v, ensure_ascii=False),
                    ),
                )

    def load_playlist_videos(self, playlist_id: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT data_json FROM videos
                WHERE playlist_id=?
                ORDER BY published_at DESC
                """,
                (playlist_id,),
            ).fetchall()
            out: List[Dict[str, Any]] = []
            for r in rows:
                try:
                    out.append(json.loads(r["data_json"]))
                except json.JSONDecodeError:
                    continue
            return out

    def load_all_videos(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT data_json FROM videos
                ORDER BY published_at DESC
                """
            ).fetchall()
            out: List[Dict[str, Any]] = []
            for r in rows:
                try:
                    out.append(json.loads(r["data_json"]))
                except json.JSONDecodeError:
                    continue
            return out

    def find_video(self, video_id: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT playlist_id, data_json
                FROM videos
                WHERE video_id=?
                LIMIT 1
                """,
                (video_id,),
            ).fetchone()
            if not row:
                return None
            try:
                return row["playlist_id"], json.loads(row["data_json"])
            except json.JSONDecodeError:
                return None

    def update_video(self, playlist_id: str, video: Dict[str, Any]):
        tags = video.get("tags", {})
        metadata = video.get("metadata", {})
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO videos (
                    video_id, playlist_id, playlist_name, title, channel, description, url,
                    published_at, duration_seconds, notes, progress_status, ai_summary,
                    tags_json, metadata_json, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    video.get("video_id"),
                    playlist_id,
                    video.get("playlist_name"),
                    video.get("title"),
                    video.get("channel"),
                    video.get("description"),
                    video.get("url"),
                    video.get("published_at"),
                    int(video.get("duration_seconds", 0) or 0),
                    video.get("notes"),
                    video.get("progress_status"),
                    video.get("ai_summary"),
                    json.dumps(tags, ensure_ascii=False),
                    json.dumps(metadata, ensure_ascii=False),
                    json.dumps(video, ensure_ascii=False),
                ),
            )

    def set_playlist_folder(self, playlist_id: str, folder: Optional[str]) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE playlists SET folder=? WHERE id=?",
                (folder, playlist_id),
            )
            return cur.rowcount > 0

    def list_folders(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT COALESCE(folder, '') AS folder, COUNT(*) AS count
                FROM playlists
                GROUP BY COALESCE(folder, '')
                ORDER BY folder ASC
                """
            ).fetchall()
            out = []
            for row in rows:
                name = row["folder"].strip()
                if name:
                    out.append({"name": name, "count": int(row["count"])})
            return out

    def analytics_summary(self) -> Dict[str, Any]:
        videos = self.load_all_videos()
        playlists = self.list_playlists()

        channels = Counter((v.get("channel") or "Unknown").strip() for v in videos)
        categories = Counter(
            (v.get("metadata", {}).get("thematic", {}).get("primary") or "unknown")
            for v in videos
        )
        progress = Counter((v.get("progress_status") or "not_started") for v in videos)
        watch_seconds = sum(int(v.get("duration_seconds", 0) or 0) for v in videos)

        return {
            "total_playlists": len(playlists),
            "total_videos": len(videos),
            "total_watch_time_seconds": watch_seconds,
            "top_channels": [{"channel": c, "count": n} for c, n in channels.most_common(10)],
            "categories": [{"category": c, "count": n} for c, n in categories.most_common()],
            "progress": dict(progress),
        }

