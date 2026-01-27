# Playlist Indexer - Bug Registry

This file tracks recurring or complex bugs encountered during development, along with their solutions and prevention strategies.

## 1. Datetime JSON Serialization Error

*   **Date Encountered**: 2026-01-26
*   **Symptoms**: 500 Error during playlist indexing. `TypeError: Object of type datetime is not JSON serializable`.
*   **Root Cause**: 
    1.  Using `json.dump()` directly on dictionaries containing `datetime` objects.
    2.  Inconsistent imports (`from datetime import datetime` vs `import datetime`) causing `AttributeError: module 'datetime' has no attribute 'utcnow'`.
*   **Solution**:
    1.  Standardized import to `import datetime`.
    2.  Replaced `datetime.utcnow()` with `datetime.datetime.utcnow()`.
    3.  Implemented `CustomJSONEncoder` to handle `datetime` objects automatically in all JSON serialization calls.
    4.  See [Test Plan](playlist_indexer_BUGS/TEST_PLAN_DATETIME_SERIALIZATION.md) for full analysis.

---

## 2. EXE Persistence Failure (API Key / Playlists Lost on Restart)

*   **Date Encountered**: 2026-01-27
*   **Symptoms**: After closing and reopening `PlaylistIndexer.exe`, API key and indexed playlists were not retained. Error: "Browser automation fallback not yet implemented. Please configure YouTube API key in config.json".
*   **Root Cause**:
    1.  Path resolution functions (`get_output_dir`) were defined *after* global module-level instantiations that depended on them (e.g., `VideoStoreAPI()`).
    2.  `config.json` was not included in PyInstaller bundled datas, so the dist folder had a default/empty config without the API key.
    3.  `playlist_indexer.py` resolved `output_dir` relative to CWD instead of the config file location.
*   **Solution**:
    1.  Moved `get_app_root()` and `get_config_path()` to top of `web_app.py` before any global instantiations.
    2.  Updated `VideoStoreAPI` instantiation to use `get_app_root()`.
    3.  Updated `playlist_indexer.spec` to include `('config.json', '.')` in datas.
    4.  Modified `playlist_indexer.py` to store absolute config path and resolve relative `output_dir` against it.
*   **Verification**: Rebuilt EXE, indexed a playlist, closed app, reopened — data persisted correctly.

---
