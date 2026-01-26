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
