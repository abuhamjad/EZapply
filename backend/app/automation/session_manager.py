"""
Owns Playwright browser lifecycle + per-platform login/cookie persistence.

Storing auth state: Playwright supports `context.storage_state(path=...)` to
save cookies + localStorage after a manual login, and
`browser.new_context(storage_state=path)` to restore it on the next run —
this is the recommended way to avoid re-logging-in every run.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from playwright.async_api import Browser, Page, async_playwright

from app.core.config import BASE_DIR
from app.core.logging import get_logger

logger = get_logger(__name__)

SESSIONS_DIR = BASE_DIR / "storage" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


class PlatformSessionManager:
    def _session_path(self, platform: str) -> Path:
        return SESSIONS_DIR / f"{platform}.json"

    @asynccontextmanager
    async def browser_session(self):
        async with async_playwright() as p:
            # headless=False during development so the user can complete
            # logins / CAPTCHAs manually the first time.
            logger.info("Launching Chromium browser session via Playwright")
            browser = await p.chromium.launch(headless=False)
            try:
                yield browser
            finally:
                await browser.close()

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
