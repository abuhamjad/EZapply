"""
Indeed-specific adapter — same interface contract as linkedin.py.
Selectors are placeholders; inspect Indeed's live DOM before use.
"""
from playwright.async_api import Page


async def ensure_logged_in(page: Page) -> None:
    await page.goto("https://secure.indeed.com/auth")


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
