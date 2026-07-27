# EZApply Backend

## Setup
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## Run
```bash
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs
SQLite DB (`app.db`) and uploaded resumes/session cookies are created automatically on first run.

## Build order (matches AGENTS.md / docs/WORKFLOWS.md)
1. `app/models/` + `app/database/connection.py` — done
2. `app/repositories/` + `app/schemas/` — done
3. `app/services/` — done (business logic)
4. `app/api/routes/` + `app/api/router.py` — done
5. `app/automation/` — **scaffolded only**. `engine.py`, `form_filler.py`,
   `session_manager.py` are structurally complete; `platforms/linkedin.py`
   and `platforms/indeed.py` have TODO stubs where real DOM selectors need
   to be filled in against each site's live markup (their DOM/class names
   are not stable enough to hardcode reliably — inspect and fill in as you build).

## What's fully working right now
- Saved Info CRUD (GET/PUT /api/v1/saved-info)
- Resume upload + basic parsing (POST /api/v1/resumes/upload)
- Bot run creation/status/stop skeleton, DB-backed (POST /api/v1/bot/start, etc.)
- Screening question learning system (DB layer + resolve endpoint)
- Application tracking + stats dashboard endpoint

## What needs your platform-specific work
- `app/automation/platforms/linkedin.py` / `indeed.py`: real selectors for
  job search results and Easy Apply / Indeed apply modals
- `BotService.get_status`: wiring `pending_question` to the latest
  unresolved `ScreeningQuestion` for a run (one extra repo query)
- Resuming a paused run after `/bot/resolve-question` (currently a TODO —
  simplest approach: re-launch `run_automation` and have the engine check
  for/consume any newly-answered `ScreeningQuestion` before continuing)
