# Implementation Plan Refractored: Playlist Navigator Pro
*Based on: docs/IMPLEMENTATION_PLAN.md | Date: 2026-02-28*

---

## 1) Why this refactor exists
The current implementation plan is strong on ideas, but weaker on execution mechanics.  
This refractored version adds:
- dependency gates
- measurable acceptance criteria
- rollout and rollback strategy
- testing requirements per milestone
- risk and observability requirements

Goal: reduce delivery risk while preserving the original feature roadmap.

---

## 2) Baseline and constraints

### Baseline (already working)
- Indexing
- Search
- Tags
- Delta sync
- Excel export
- Flask backend + vanilla JS frontend
- JSON file storage

### Constraints and fixed decisions
1. Keep vanilla JS frontend; do not revive React prototype.
2. Archive Liquid Dynamics integration work.
3. Treat SQLite migration as a hard gate before data-heavy analytics/AI persistence.
4. Favor small, shippable slices over large feature batches.

---

## 3) Priority model
Use this scoring model for backlog ordering inside each milestone:
- User value (1-5)
- Engineering effort (1-5, lower is better)
- Dependency criticality (1-5)
- Risk (1-5, lower is better)

Suggested score:
`priority_score = value + dependency_criticality - effort - risk`

---

## 4) Delivery stages and gates

## Stage A - UX quick wins
Scope:
- Dark mode
- Keyboard shortcuts
- Smart duration/discovery filters
- List/grid view toggle

Files:
- `templates/index.html`
- `static/js/app.js`
- `static/css/style.css` (+ theme files as needed)

Acceptance criteria:
- All settings persist via `localStorage`.
- No regressions in existing search and playlist interactions.
- Manual smoke test checklist passes on desktop and mobile widths.

Gate A exit:
- All Stage A items shipped without backend API changes.

---

## Stage B - Core workflow UX
Scope:
- Watch progress tracking
- Personal notes
- Search improvements (description toggle + AND/OR logic + highlighting)
- Saved searches/history
- Playlist folders/collections
- LLM assistant MVP

Files:
- `templates/index.html`
- `static/js/app.js`
- `web_app.py`
- `execution/excel_exporter.py`
- `execution/metadata_enricher.py`
- `output/playlists.json` (schema extension for folders)

New/changed API contracts:
- `POST /api/videos/<id>/notes` (if backend notes enabled)
- `POST /api/playlists/<id>/folder`
- `GET /api/folders`
- `POST /api/assistant/chat`

Acceptance criteria:
- Existing endpoints remain backward compatible.
- Folder schema migration keeps old playlists readable.
- Assistant failures are graceful (no 500 crash path visible to user).

Gate B exit:
- Core UX features stable on JSON storage at current scale.

---

## Stage C - Data foundation (hard gate)
Scope:
- Migrate storage to SQLite.
- Add migration utility from JSON -> SQLite.
- Update data access layer and endpoint read paths.
- Keep JSON export as backup.

Files:
- `execution/video_store_api.py`
- `web_app.py`
- `execution/db.py` (new)
- `execution/migrate_sqlite.py` (new)

Schema targets:
- `playlists`
- `videos`
- `tags`
- `user_progress`
- `user_notes`
- `folders`

Acceptance criteria:
- Migration parity: row counts and key fields match source JSON.
- Endpoint parity: existing API behavior preserved unless explicitly documented.
- Performance baseline improved on larger datasets.

Rollback strategy:
- Keep JSON source untouched until migration verification passes.
- Add feature flag/config switch: JSON mode vs SQLite mode.

Gate C exit:
- SQLite is default runtime store.
- Rollback path documented and tested.

---

## Stage D - Analytics and sync automation
Depends on Stage C.

Scope:
- Analytics summary endpoint + UI section
- Scheduled auto-sync with interval config

Files:
- `web_app.py`
- `templates/index.html`
- `static/js/app.js`
- `config.json`

New API:
- `GET /api/analytics/summary`

Acceptance criteria:
- Aggregates are correct against sampled known dataset.
- Scheduler is idempotent and observable.
- UI shows last-sync status per playlist.

Gate D exit:
- Analytics and scheduler stable for daily use.

---

## Stage E - AI intelligence features
Depends on Stage C, recommended after Stage D stabilization.

Scope:
- Auto-tag suggestions
- AI summaries
- Similar video recommendations
- Mind map enhancements
- Difficulty progression recommendations

Files:
- `execution/metadata_enricher.py`
- `web_app.py`
- `templates/index.html`
- `static/js/app.js`

Acceptance criteria:
- AI features are optional and do not break core UX on API failure.
- Latency and cost are measurable (logging/metrics).
- Generated fields are cached and safe to re-use.

Gate E exit:
- AI features meet quality threshold and operational budget.

---

## 5) Testing strategy by stage

## Stage A
- Manual UI smoke tests.
- Basic JS behavior tests for toggles/shortcuts (where test harness exists).

## Stage B
- Endpoint tests for new routes in `tests/integration`.
- UI flow checks for persistence and combined filters.
- Regression checks for search and playlist navigation.

## Stage C
- Migration parity tests (counts + sampled record diff).
- Data access unit tests for SQLite-backed queries.
- API regression test pass before switching default store.

## Stage D
- Analytics endpoint correctness tests.
- Scheduler tests: trigger, repeat-run, and failure path behavior.

## Stage E
- AI response schema validation.
- Fallback behavior tests (upstream API unavailable).
- Cost/latency logging verification.

---

## 6) Observability and reliability requirements
Add these before Stage C cutover:
- Structured logs for endpoint errors and long-running tasks.
- Error counters by route.
- Sync job outcome logging (success/fail/duration).
- Migration report artifact with counts and mismatches.

---

## 7) Security and data safety checks
- Never log API keys or full secret payloads.
- Validate and sanitize user-provided text used for highlighting/rendering.
- Use atomic writes for any interim JSON updates (temp file + rename).
- Back up registry and data files before migration execution.

---

## 8) Risk register and mitigations
1. JSON corruption before SQLite cutover.
   - Mitigation: atomic writes + defensive parsing + skip bad file with warning.
2. `web_app.py` growth/regression risk.
   - Mitigation: endpoint-focused tests before/after each feature slice.
3. AI scope creep.
   - Mitigation: strict MVP definitions and acceptance criteria.
4. Migration uncertainty.
   - Mitigation: dry-run mode + parity report + rollback switch.

---

## 9) Execution order (recommended)
1. Stage A complete
2. Stage B: progress + notes first
3. Stage B: search + folders + saved searches
4. Stage B: assistant MVP
5. Stage C hard gate (SQLite)
6. Stage D analytics/scheduler
7. Stage E AI extensions

---

## 10) Deferred / archived items
- Liquid Dynamics integration
- React frontend rewrite
- Multi-user/auth stack
- Watch party collaboration
- Voice search
- Audio-only mode

---

## 11) Definition of done (plan level)
Plan execution is considered complete when:
- Stages A through D are shipped and stable.
- Stage E is either shipped incrementally or explicitly deferred by documented decision.
- SQLite is production default with validated migration and rollback path.
- Critical endpoint and UX regressions are covered by automated tests.
