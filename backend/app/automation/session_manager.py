"""
Owns Playwright browser lifecycle + per-platform login/cookie persistence.

Storing auth state: Playwright supports `context.storage_state(path=...)` to
save cookies + localStorage after a manual login, and
`browser.new_context(storage_state=path)` to restore it on the next run —
this is the recommended way to avoid re-logging-in every run.
"""
import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from playwright.async_api import Browser, Page, async_playwright

from app.core.config import BASE_DIR, settings
from app.core.logging import get_logger

# Last-resort guard: if something else in the stack reset the event loop policy
# after run.py set it, this re-applies it before Playwright can launch.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

logger = get_logger(__name__)

SESSIONS_DIR = BASE_DIR / "storage" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


class PlatformSessionManager:
    def _session_path(self, platform: str) -> Path:
        return SESSIONS_DIR / f"{platform}.json"

    @asynccontextmanager
    async def browser_session(self):
        headless = settings.PLAYWRIGHT_HEADLESS
        try:
            async with async_playwright() as p:
                logger.info(
                    "Launching Chromium browser session via Playwright (headless=%s)",
                    headless,
                )
                browser = await p.chromium.launch(headless=headless)
                try:
                    yield browser
                finally:
                    await browser.close()
        except Exception:
            logger.exception(
                "[session_manager] Playwright launch failed — "
                "if you see NotImplementedError, start the server with "
                "'python run.py' instead of 'uvicorn app.main:app ...'"
            )
            raise

    async def get_authenticated_page(self, browser: Browser, platform: str) -> Page:
        session_path = self._session_path(platform)

        if session_path.exists():
            context = await browser.new_context(storage_state=str(session_path))
        else:
            # No saved session: open a fresh context, the platform adapter's
            # `ensure_logged_in()` should prompt the user to log in manually,
            # then we persist the resulting storage_state for next time.
            context = await browser.new_context()

        page = await context.new_page()
        return page

    async def save_session(self, page: Page, platform: str) -> None:
        await page.context.storage_state(path=str(self._session_path(platform)))
        logger.info("Saved session state for %s", platform)
