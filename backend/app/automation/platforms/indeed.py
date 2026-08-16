"""
Indeed-specific adapter — same interface contract as linkedin.py.
Selectors are placeholders; inspect Indeed's live DOM before use.
"""
import asyncio
from playwright.async_api import Page


async def ensure_logged_in(page: Page, timeout_seconds: int = 60, on_timeout_callback=None) -> bool:
    """
    Navigate to Indeed login and wait for user to sign in.
    Checks every 2 seconds if login succeeded.
    
    Args:
        page: Playwright page object
        timeout_seconds: Max seconds to wait for login (default: 60)
        on_timeout_callback: Optional async callback(seconds_remaining) called each check
    
    Returns:
        bool: True if login detected, False if timeout reached without login.
    """
    await page.goto("https://secure.indeed.com/auth")
    
    start_time = asyncio.get_event_loop().time()
    check_interval = 2
    
    while asyncio.get_event_loop().time() - start_time < timeout_seconds:
        try:
            # Check for logged-in indicators on Indeed
            selectors = [
                ".icl-Header-userProfileMenuPrimary",
                "[data-testid='userProfile']",
                ".navUserMenu",
                ".gnav-user-menu"
            ]
            
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        return True
                except:
                    pass
        except:
            pass
        
        # Call callback if provided
        if on_timeout_callback:
            elapsed = asyncio.get_event_loop().time() - start_time
            seconds_remaining = max(0, timeout_seconds - elapsed)
            try:
                await on_timeout_callback(int(seconds_remaining))
            except:
                pass
        
        await asyncio.sleep(check_interval)
    
    return False


async def search_jobs(page: Page, keywords: list[str], location: str | None = None, job_type: str | None = None, min_salary: int | None = None) -> list[dict]:
    jobs: list[dict] = []
    for keyword in keywords:
        search_url = f"https://www.indeed.com/jobs?q={keyword.replace(' ', '+')}"
        if location:
            search_url += f"&l={location.replace(' ', '+')}"
        await page.goto(search_url)
        try:
            await page.wait_for_selector("#mosaic-provider-jobcards", timeout=10_000)
        except Exception:
            pass
        # TODO: extract job cards -> title/company/href
    return jobs


async def open_application_modal(page: Page, job: dict) -> None:
    await page.goto(job["url"])
    # TODO: click "Apply now" button


async def read_form_fields(page: Page) -> list[dict]:
    return []


async def fill_field(page: Page, field: dict, value: str) -> None:
    await page.fill(field["selector"], value)


async def submit(page: Page) -> None:
    pass
