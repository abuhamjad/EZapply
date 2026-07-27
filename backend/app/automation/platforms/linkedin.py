"""
LinkedIn-specific adapter. Implements the interface that engine.py /
form_filler.py expect: search_jobs, read_form_fields, fill_field, submit.

All CSS selectors below are placeholders — inspect LinkedIn's live DOM
(it changes often) and update accordingly before use.
"""
from playwright.async_api import Page


async def ensure_logged_in(page: Page) -> None:
    await page.goto("https://www.linkedin.com/login")
    # If already authenticated via restored session, this redirects to feed.
    # Otherwise, pause here (headless=False) so the user can log in manually,
    # then engine.py should call session_manager.save_session(page, "linkedin").


async def search_jobs(page: Page, keywords: list[str]) -> list[dict]:
    """Returns a list of {title, company, url} dicts for matching listings."""
    jobs: list[dict] = []
    for keyword in keywords:
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}"
        await page.goto(search_url)
        await page.wait_for_selector(".jobs-search-results-list", timeout=10_000)

        # TODO: query .job-card-container elements, extract title/company/href
        # cards = await page.query_selector_all(".job-card-container")

    return jobs


async def open_application_modal(page: Page, job: dict) -> None:
    await page.goto(job["url"])
    # TODO: click "Easy Apply" button
    # await page.click("button.jobs-apply-button")


async def read_form_fields(page: Page) -> list[dict]:
    """Returns [{label, type, selector}, ...] for the current modal step."""
    # TODO: query the Easy Apply modal's input/select/radio/checkbox elements
    return []


async def fill_field(page: Page, field: dict, value: str) -> None:
    # TODO: dispatch based on field["type"] (text/select/radio/checkbox)
    await page.fill(field["selector"], value)


async def submit(page: Page) -> None:
    # TODO: click through Easy Apply's "Next" steps then final "Submit application"
    pass
