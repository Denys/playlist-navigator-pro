#!/usr/bin/env python3
"""
Migrate JSON storage (output/playlists.json + *_data.json files) into SQLite.
"""

import argparse
import json
import os
from typing import Any, Dict, List

from execution.db import SQLiteStore
from execution.io_utils import read_json_file


def _load_json_registry(output_dir: str) -> Dict[str, Any]:
    registry_path = os.path.join(output_dir, "playlists.json")
    return read_json_file(registry_path, {"playlists": [], "total_playlists": 0, "total_videos": 0})


def _load_playlist_videos(playlist: Dict[str, Any]) -> List[Dict[str, Any]]:
    data_file = os.path.join(playlist.get("output_dir", ""), f"{playlist.get('id')}_data.json")
    if not data_file:
        return []
    return read_json_file(data_file, [])


def migrate(output_dir: str, db_path: str, reset: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    registry = _load_json_registry(output_dir)
    playlists = registry.get("playlists", [])

    json_video_count = 0
    playlist_video_map: Dict[str, int] = {}
    all_payloads: List[Dict[str, Any]] = []

    for p in playlists:
        videos = _load_playlist_videos(p)
        playlist_video_map[p.get("id", "")] = len(videos)
        json_video_count += len(videos)
        all_payloads.append({"playlist": p, "videos": videos})

    if dry_run:
        return {
            "mode": "dry_run",
            "json_total_playlists": len(playlists),
            "json_total_videos": json_video_count,
            "db_total_playlists": None,
            "db_total_videos": None,
            "playlist_video_map": playlist_video_map,
            "parity_ok": None,
        }

    store = SQLiteStore(db_path)
    if reset:
        store.clear_all()

    for item in all_payloads:
        playlist = dict(item["playlist"])
        videos = item["videos"]
        playlist["video_count"] = len(videos)
        store.upsert_playlist(playlist)
        store.save_playlist_videos(playlist.get("id", ""), playlist.get("name", ""), videos)

    db_registry = store.load_registry()
    db_total_playlists = int(db_registry.get("total_playlists", 0))
    db_total_videos = int(db_registry.get("total_videos", 0))

    parity_ok = (db_total_playlists == len(playlists)) and (db_total_videos == json_video_count)
    return {
        "mode": "migrated",
        "json_total_playlists": len(playlists),
        "json_total_videos": json_video_count,
        "db_total_playlists": db_total_playlists,
        "db_total_videos": db_total_videos,
        "playlist_video_map": playlist_video_map,
        "parity_ok": parity_ok,
        "db_path": db_path,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="output", help="JSON output directory (default: output)")
    parser.add_argument("--db-path", default=os.path.join("output", "playlist_indexer.db"), help="SQLite DB path")
    parser.add_argument("--reset", action="store_true", help="Clear existing DB tables before migrate")
    parser.add_argument("--dry-run", action="store_true", help="Only scan JSON and report counts")
    args = parser.parse_args()

    report = migrate(
        output_dir=args.output_dir,
        db_path=args.db_path,
        reset=args.reset,
        dry_run=args.dry_run,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if (report.get("parity_ok") is not False) else 2)


if __name__ == "__main__":
    main()

