Implementation Plan: Playlist Navigator Pro — Feature Roadmap
Source: docs/Brainstorm.md

Context
Playlist Navigator Pro is a production-ready YouTube playlist management tool with a Flask backend, vanilla JS frontend (Glassmorphic UI), and JSON file storage. The core is stable: indexing, search, tags, delta sync, and Excel export all work. This plan converts the brainstorm into a phased, actionable roadmap ordered by effort-to-value ratio, grounded in the existing architecture.

Key constraints:

JSON storage scales poorly beyond ~100K videos → SQLite migration is a prerequisite gate for data-heavy features
Liquid Dynamics animation framework (~4,800 lines, 0% integrated) — decision: archive it (sunk cost; 16–20 more hours to integrate is not justified)
React frontend prototype (30% complete, 0% integrated) — abandoned, stay with vanilla JS
Phase 1 — Quick Wins (Low effort · High value)
Target: 1–2 days each. No architectural changes needed.

1.1 Dark Mode
Add a data-theme attribute toggle on <body> in templates/index.html
Define CSS variables for light / dark palettes in static/css/
Persist preference with localStorage.setItem('theme', ...)
Toggle button in the nav bar (moon/sun icon)
1.2 Keyboard Shortcuts
In static/js/app.js, add a document.addEventListener('keydown', ...) handler
/ → focus search input
J / K → navigate video list rows
Enter → open selected video in YouTube
Esc → close modals / clear search
1.3 Smart Duration & Discovery Filters
Existing data model already has duration_seconds, view_count, like_count, published_at
Add a filter bar UI above search results in templates/index.html
Implement client-side JS filter functions in static/js/app.js:
Quick Watch duration_seconds < 300
Coffee Break 300–900s
Deep Dive >= 1800s
Recently Added indexed in last 7 days
Viral Hits view_count >= 1_000_000
Hidden Gems view_count < 10_000 but high engagement ratio
Fresh Content published_at within 30 days
1.4 Compact / Grid View Toggle
Add two icon buttons (list icon, grid icon) in the playlist/search views
Toggle between .view-list and .view-grid CSS classes
localStorage persists the preference
Phase 2 — Core UX Features (Medium effort · High value)
Target: 2–5 days each. Minimal backend changes.

2.1 Watch Progress Tracking
Storage: localStorage keyed by video_id → { status: 'not_started' | 'in_progress' | 'completed', timestamp }
UI: Three-state button on each video card (circle → half-circle → checkmark)
Filter integration: "Not Started / In Progress / Completed" filter pills (Phase 1 filter bar)
Future: Migrate to backend when SQLite lands (Phase 3)
2.2 Personal Notes per Video
Storage: localStorage['notes_${video_id}'] → string
UI: A collapsible notes panel on each video row, textarea input, auto-save on blur
Backend (optional v2): POST /api/videos/<id>/notes → writes to a user_data.json sidecar file
Export: Include notes column in Excel export via execution/excel_exporter.py
2.3 Full-Text Description Search
Current search in web_app.py already searches descriptions (confirm field inclusion)
Improve: add boolean AND/OR logic, highlight matched terms in results
Add "Search in descriptions" toggle checkbox in the search bar UI
2.4 Saved Searches & Search History
localStorage['search_history'] → array of last 20 queries
Show history dropdown when search box is focused (empty query)
"Save this search" pin icon → localStorage['saved_searches'] → named queries
Saved searches panel in sidebar or search tab header
2.5 Playlist Folders / Collections
Data: Add folder field to playlist registry in output/playlists.json
Backend: POST /api/playlists/<id>/folder → updates registry
UI: Folder sidebar in Playlists tab; drag playlist cards into folders
New API route in web_app.py: GET /api/folders → list all folders
Phase 3 — Architecture & Analytics (Higher effort · Foundation work)
Target: 1–2 weeks. Enables Phase 4 features.

3.1 SQLite Backend Migration ⚠️ Prerequisite Gate
Replace JSON file storage with SQLite via sqlite3 (stdlib) or SQLAlchemy
Schema: playlists, videos, tags, user_progress, user_notes, folders
Write migration script: reads all output/**/*_data.json → inserts into DB
Update execution/video_store_api.py to query SQLite
Retain JSON export for backup/portability
This unlocks: fast filtering, full-text index (FTS5), analytics queries
3.2 Dashboard Stats & Analytics
New tab "Analytics" or section in existing Playlists tab
Cards: total videos, total watch time (sum duration_seconds), videos per category
Channel leaderboard (top 10 channels by video count)
Progress tracker: % completed per playlist (uses Phase 2.1 progress data)
Tag cloud: frequency-weighted interactive tag visualization (D3.js — already imported)
Backend: GET /api/analytics/summary → aggregate query on SQLite
3.3 Scheduled Auto-Sync
Add APScheduler or a background thread loop to web_app.py
Weekly cron: call existing DeltaSync in execution/delta_sync.py for each playlist
Config option in config.json: "auto_sync_interval_days": 7
UI: last-synced timestamp on playlist cards, manual "Sync Now" button
Phase 4 — Intelligence & AI Features (Advanced · Deferred)
Target: Post-Phase 3. Requires stable data layer.

4.1 Auto-Tag Suggestions (LLM-based)
Extend execution/metadata_enricher.py
Call Gemini/Claude API with video title + description → suggest 3–5 tags
Surface in UI as "Suggested Tags" chips with one-click accept
4.2 Internal LLM Assistant
Chat panel (collapsible sidebar) powered by Gemini API
Context: currently visible playlist/search results injected as system prompt
Queries: "Summarize what's in this playlist", "Find me beginner Python videos"
New route: POST /api/assistant/chat
4.3 AI Video Summaries
For each video: call LLM with description → generate TL;DR (2–3 sentences)
Store in SQLite videos table as ai_summary column
Display as collapsible "Summary" row under video title
4.4 Smart Recommendations ("Similar To…")
TF-IDF or embedding similarity on tags + description
GET /api/videos/<id>/similar → top 5 similar videos
"More like this" button on video cards
4.5 Mind Map Enhancements
Cluster by channel (D3 force-directed groups)
Click node → filter main video view
Zoom to fit on open
Export as SVG/PNG
Deferred / Archived
Feature	Reason
Liquid Dynamics integration	Sunk cost; 16–20h to integrate. Archive liquid-dynamics/ folder.
React frontend	30% prototype, 0% value. Stick with vanilla JS.
Collaborative Playlists / Watch Party	Requires multi-user auth infrastructure. Out of scope.
Voice Search	High complexity, low ROI for local tool.
Audio-Only Mode	Out of scope for playlist navigator.
Multi-User Support	Single-user tool; multi-user needs full auth rewrite.
Files Modified Per Phase
Phase	Files Touched
1.1 Dark Mode	templates/index.html, static/css/, static/js/app.js
1.2 Keyboard Shortcuts	static/js/app.js
1.3 Smart Filters	static/js/app.js, templates/index.html
1.4 View Toggle	static/js/app.js, templates/index.html, static/css/
2.1 Progress Tracking	static/js/app.js, templates/index.html
2.2 Personal Notes	static/js/app.js, templates/index.html, web_app.py, execution/excel_exporter.py
2.3 Full-Text Search	web_app.py, static/js/app.js
2.4 Saved Searches	static/js/app.js, templates/index.html
2.5 Playlist Folders	web_app.py, static/js/app.js, templates/index.html
3.1 SQLite Migration	execution/video_store_api.py, web_app.py, new execution/db.py, new migrate.py
3.2 Analytics	web_app.py, static/js/app.js, templates/index.html
3.3 Auto-Sync	web_app.py, config.json
4.x AI Features	execution/metadata_enricher.py, web_app.py, static/js/app.js
Implementation Order (Recommended)
Phase 1 (all four) — ship fast wins first for immediate user value
Phase 2.1 Watch Progress + 2.2 Personal Notes — highest learning value
Phase 2.3–2.5 — search and organization improvements
Phase 3.1 SQLite — foundational; do before any analytics or AI work
Phase 3.2–3.3 — analytics and auto-sync on top of SQLite
Phase 4 — AI features last, when foundation is solid
Verification
Each feature can be verified by:

Running python web_app.py and testing in browser at http://localhost:5000
Phase 1–2 features: purely client-side, verify via browser devtools + localStorage inspection
Phase 3.1 migration: run python migrate.py, verify row counts match JSON file counts
Phase 3.2 analytics: check /api/analytics/summary JSON response, verify chart renders
Phase 4 AI: check API responses contain non-empty ai_summary / suggested_tags fields