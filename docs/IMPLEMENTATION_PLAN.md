# Implementation Plan: Playlist Navigator Pro — Feature Roadmap
*Source: docs/Brainstorm.md · Created: 2026-02-28*

---

## Context

Playlist Navigator Pro is a production-ready YouTube playlist management tool with a Flask backend, vanilla JS frontend (Glassmorphic UI), and JSON file storage. The core is stable: indexing, search, tags, delta sync, and Excel export all work. This plan converts the brainstorm into a phased, actionable roadmap ordered by effort-to-value ratio, grounded in the existing architecture.

**Key constraints:**
- JSON storage scales poorly beyond ~100K videos → SQLite migration is a prerequisite gate for data-heavy features
- Liquid Dynamics animation framework (~4,800 lines, 0% integrated) — decision: **archive it** (sunk cost; 16–20 more hours to integrate is not justified)
- React frontend prototype (30% complete, 0% integrated) — **abandoned**, stay with vanilla JS

---

## Phase 1 — Quick Wins
*Low effort · High value · 1–2 days each · No architectural changes needed*

### 1.1 Dark Mode
- Add a `data-theme` attribute toggle on `<body>` in `templates/index.html`
- Define CSS variables for `light` / `dark` palettes in `static/css/`
- Persist preference with `localStorage`
- Toggle button in the nav bar (moon/sun icon)

### 1.2 Keyboard Shortcuts
- Add a `document.addEventListener('keydown', ...)` handler in `static/js/app.js`
- `/` → focus search input
- `J / K` → navigate video list rows
- `Enter` → open selected video in YouTube
- `Esc` → close modals / clear search

### 1.3 Smart Duration & Discovery Filters
- Existing data model already has `duration_seconds`, `view_count`, `like_count`, `published_at`
- Add a filter pill bar above search results in `templates/index.html`
- Implement client-side JS filter functions in `static/js/app.js`:

| Filter | Logic |
|--------|-------|
| Quick Watch | `duration_seconds < 300` |
| Coffee Break | `300–900s` |
| Deep Dive | `>= 1800s` |
| Recently Added | indexed in last 7 days |
| Viral Hits | `view_count >= 1,000,000` |
| Hidden Gems | `view_count < 10,000` but high engagement ratio |
| Fresh Content | `published_at within 30 days` |

### 1.4 Compact / Grid View Toggle
- Two icon buttons (list / grid) in playlist and search views
- Toggle `.view-list` / `.view-grid` CSS classes
- `localStorage` persists the preference

---

## Phase 2 — Core UX Features
*Medium effort · High value · 2–5 days each · Minimal backend changes*

### 2.1 Watch Progress Tracking
- **Storage:** `localStorage` keyed by `video_id` → `{ status: 'not_started' | 'in_progress' | 'completed' }`
- **UI:** Three-state button on each video card (○ → ◑ → ✓)
- **Filters:** "Not Started / In Progress / Completed" filter pills (integrates with Phase 1 filter bar)
- **Future:** Migrate to backend when SQLite lands (Phase 3)

### 2.2 Personal Notes per Video
- **Storage:** `localStorage['notes_${video_id}']`
- **UI:** Collapsible notes panel on each video row, textarea with auto-save on blur
- **Backend (v2):** `POST /api/videos/<id>/notes` → writes to a `user_data.json` sidecar
- **Export:** Include notes column in Excel export via `execution/excel_exporter.py`

### 2.3 Full-Text Description Search Improvements
- Confirm description field is included in `web_app.py` search route
- Add boolean AND/OR query logic
- Highlight matched terms in results
- Add "Search in descriptions" toggle checkbox

### 2.4 Saved Searches & Search History
- `localStorage['search_history']` → array of last 20 queries
- Dropdown shown on focus (empty query) with history list
- "Save this search" pin icon → `localStorage['saved_searches']` → named queries
- Saved searches panel in search tab header

### 2.5 Playlist Folders / Collections
- **Data:** Add `folder` field to playlist registry in `output/playlists.json`
- **Backend:** `POST /api/playlists/<id>/folder` → update registry; `GET /api/folders`
- **UI:** Folder sidebar in Playlists tab; drag playlist cards into folders

### 2.6 LLM Assistant (Content Search & Analysis)
- Chat panel powered by Gemini API
- Context: currently visible playlist/search results injected into system prompt
- Example queries: "Summarize this playlist", "Find beginner Python videos", "What topics overlap?"
- New backend route: `POST /api/assistant/chat`
- Extends `execution/metadata_enricher.py` with LLM call wrapper

---

## Phase 3 — Architecture & Analytics
*Higher effort · Foundation work · 1–2 weeks*

### 3.1 SQLite Backend Migration ⚠️ Prerequisite Gate
- Replace JSON file storage with SQLite (`sqlite3` stdlib or SQLAlchemy)
- Schema: `playlists`, `videos`, `tags`, `user_progress`, `user_notes`, `folders`
- Write `migrate.py`: reads all `output/**/*_data.json` → inserts into DB
- Update `execution/video_store_api.py` to query SQLite (FTS5 for full-text)
- Retain JSON export for backup/portability
- **Unlocks:** fast filtering, analytics queries, AI feature storage

### 3.2 Dashboard Stats & Analytics
- New "Analytics" section or tab
- Stats cards: total videos, total watch time, videos per category
- Channel leaderboard (top 10 by video count)
- Progress tracker: % completed per playlist
- Tag cloud: frequency-weighted interactive visualization (D3.js — already imported)
- Backend: `GET /api/analytics/summary`

### 3.3 Scheduled Auto-Sync
- Add APScheduler or background thread loop to `web_app.py`
- Weekly cron: call existing `DeltaSync` in `execution/delta_sync.py` for each playlist
- Config option in `config.json`: `"auto_sync_interval_days": 7`
- UI: last-synced timestamp on playlist cards + manual "Sync Now" button

---

## Phase 4 — AI & Intelligence Features
*Advanced · Post-Phase 3 · Requires stable SQLite data layer*

### 4.1 Auto-Tag Suggestions
- Extend `execution/metadata_enricher.py`
- Call Gemini API with title + description → suggest 3–5 tags
- Surface as "Suggested Tags" chips with one-click accept in UI

### 4.2 AI Video Summaries
- LLM generates TL;DR (2–3 sentences) from description per video
- Store in SQLite `videos.ai_summary` column
- Display as collapsible "Summary" row under video title

### 4.3 Smart Recommendations ("Similar To…")
- TF-IDF or embedding similarity on tags + description
- `GET /api/videos/<id>/similar` → top 5 similar videos
- "More like this" button on video cards

### 4.4 Mind Map Enhancements
- Cluster nodes by channel (D3 force-directed groups)
- Click node → filter main video view
- Zoom-to-fit on open
- Export as SVG/PNG

### 4.5 Difficulty Progress Tracker
- Tag videos `beginner` / `intermediate` / `advanced` (via LLM or user)
- Visual skill progression timeline per topic
- Recommends "next step" based on completed videos

---

## Deferred / Archived

| Feature | Reason |
|---------|--------|
| Liquid Dynamics integration | Sunk cost; 16–20h more to integrate. Archive `liquid-dynamics/` folder. |
| React frontend | 30% prototype, 0% value delivered. Stay with vanilla JS. |
| Collaborative Playlists / Watch Party | Requires multi-user auth infrastructure. Out of scope. |
| Voice Search | High complexity, low ROI for a local tool. |
| Audio-Only Mode | Out of scope for playlist navigator. |
| Multi-User Support | Needs full auth rewrite. Single-user focus for now. |

---

## Files Modified Per Phase

| Phase | Files |
|-------|-------|
| 1.1 Dark Mode | `templates/index.html`, `static/css/`, `static/js/app.js` |
| 1.2 Keyboard Shortcuts | `static/js/app.js` |
| 1.3 Smart Filters | `static/js/app.js`, `templates/index.html` |
| 1.4 View Toggle | `static/js/app.js`, `templates/index.html`, `static/css/` |
| 2.1 Progress Tracking | `static/js/app.js`, `templates/index.html` |
| 2.2 Personal Notes | `static/js/app.js`, `templates/index.html`, `web_app.py`, `execution/excel_exporter.py` |
| 2.3 Search Improvements | `web_app.py`, `static/js/app.js` |
| 2.4 Saved Searches | `static/js/app.js`, `templates/index.html` |
| 2.5 Playlist Folders | `web_app.py`, `static/js/app.js`, `templates/index.html` |
| 2.6 LLM Assistant | `web_app.py`, `execution/metadata_enricher.py`, `static/js/app.js`, `templates/index.html` |
| 3.1 SQLite Migration | `execution/video_store_api.py`, `web_app.py`, new `execution/db.py`, new `migrate.py` |
| 3.2 Analytics | `web_app.py`, `static/js/app.js`, `templates/index.html` |
| 3.3 Auto-Sync | `web_app.py`, `config.json` |
| 4.x AI Features | `execution/metadata_enricher.py`, `web_app.py`, `static/js/app.js` |

---

## Recommended Implementation Order

1. **Phase 1** (all four) — ship fast wins first for immediate value
2. **2.1 + 2.2** Watch Progress & Personal Notes — highest learning value
3. **2.3 – 2.5** Search and organization improvements
4. **2.6** LLM Assistant — integrates with existing enricher infrastructure
5. **3.1 SQLite** — foundational; complete before analytics or AI storage work
6. **3.2 + 3.3** Analytics and auto-sync on top of SQLite
7. **Phase 4** — AI features last, when foundation is solid

---

## Verification

| Phase | How to Test |
|-------|-------------|
| Phase 1–2 | `python web_app.py` → browser at `http://localhost:5000`; inspect `localStorage` via devtools |
| 3.1 SQLite | Run `python migrate.py`; verify row counts match JSON source counts |
| 3.2 Analytics | Check `/api/analytics/summary` JSON; verify charts render correctly |
| 3.3 Auto-Sync | Check scheduled job fires; verify playlist `last_synced` timestamp updates |
| Phase 4 AI | Check API responses contain non-empty `ai_summary` / `suggested_tags` fields |
