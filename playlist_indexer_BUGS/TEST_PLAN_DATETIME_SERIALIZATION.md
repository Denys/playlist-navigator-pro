# Test Plan: Datetime Serialization & Import Stability

**Date**: 2026-01-26
**Subject**: Analysis of "JSON not serializable" and "AttributeError" in `datetime` module.

## 1. Problem Origins

The project encountered two distinct but related errors during the playlist indexing process:

### Error A: `Object of type datetime is not JSON serializable`
*   **Origin**: The Python standard `json` library cannot natively serialize `datetime` objects.
*   **Trigger**: In `web_app.py`, the `playlist_info` dictionary contained `datetime` objects (e.g., `created_at`) which were passed directly to `json.dump()`.
*   **Why it happened**: While `execution/models.py` uses Pydantic (which handles serialization), the `web_app.py` was constructing raw dictionaries and writing them to disk manually.

### Error B: `module 'datetime' has no attribute 'utcnow'`
*   **Origin**: Variable shadowing due to import style.
*   **Trigger**: The code used `from datetime import datetime`. This made the symbol `datetime` refer to the *class*, not the *module*.
*   **Conflict**: When code attempted to call `datetime.date` or other module-level attributes (or when refactoring changed usages), the namespace collision caused common attributes to be missing.

---

## 2. Test Plan for Verification

To ensure these errors are fully resolved and won't recur, we will execute the following tests:

### Test Case 1: Registry Serialization (Unit Test)
*   **Goal**: Ensure `register_playlist` generates valid JSON.
*   **Steps**:
    1.  Mock the file system.
    2.  Call `register_playlist` with a `datetime` object in the data.
    3.  Verify `json.dump` succeeds without raising `TypeError`.

### Test Case 2: Import Namespace Integrity (Static Analysis)
*   **Goal**: Ensure no conflicting imports exist.
*   **Steps**:
    1.  Scan all files for `from datetime import datetime`.
    2.  Fail if found. Enforce `import datetime` style project-wide.

### Test Case 3: End-to-End Indexing
*   **Goal**: Verify the actual user workflow.
*   **Steps**:
    1.  Start server.
    2.  Submit "Index Playlist" request.
    3.  Monitor logs for 500 errors.
    4.  Verify `playlists.json` is written to disk.

---

## 3. Smart Solutions (Prevention)

The "fix it as it breaks" approach is fragile. Here are robust architectural solutions:

### Solution A: Custom JSON Encoder (Recommended)
Instead of manually converting `.isoformat()` every time (which is prone to human error—missing one field breaks the app), subclass `JSONEncoder`.

```python
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super().default(obj)

# Usage
json.dump(data, f, cls=DateTimeEncoder)
```

### Solution B: Global Pydantic Models
Stop using raw dictionaries in `web_app.py`. Define a `PlaylistRegistry` model in `models.py`.

```python
class PlaylistRegistryEntry(BaseModel):
    id: str
    created_at: datetime  # Pydantic handles this automatically
    ...

# Usage
entry = PlaylistRegistryEntry(...)
json.dump(entry.model_dump(mode='json'), f)
```

### Solution C: Linting Rules
Add a generic test or lint rule that forbids `from datetime import datetime` to prevent future namespace confusion.

---

## 4. Recommandation

We have currently applied **Manual Fixes** (converting to ISO strings inline).
To prevent regression, I recommend implementing **Solution A (Custom JSON Encoder)** in `web_app.py` as it provides immediate safety for any future datetime fields added to the dictionary.
