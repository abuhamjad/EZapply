"""
Windows-safe uvicorn entrypoint.

Run with:  python run.py
(instead of: uvicorn app.main:app --reload --port 8000)

Why this file exists
--------------------
On Windows, asyncio defaults to SelectorEventLoop which cannot create
subprocesses.  Playwright launches Chromium via asyncio.create_subprocess_exec,
so it raises NotImplementedError under SelectorEventLoop.

Setting WindowsProactorEventLoopPolicy here (before uvicorn creates its loop)
is the only reliable fix.  Setting it inside app/main.py is too late when the
--reload watcher is involved, because uvicorn's reloader creates child
processes that start their own loops before app/main.py is evaluated.
"""
import sys
import asyncio

# ── MUST be first, before any uvicorn / FastAPI / anyio import ──────────────
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# ────────────────────────────────────────────────────────────────────────────

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        # Do NOT set loop="uvloop" — uvloop doesn't exist on Windows.
        # Let uvicorn pick the correct loop via "auto".
        loop="auto",
    )
