"""
LinkedIn-specific adapter.
"""
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeout

async def ensure_logged_in(page: Page) -> None:
    await page.goto("https://www.linkedin.com/login")
    try:
        # Wait for the feed or the nav bar user photo to ensure auth success
        await page.wait_for_selector(".feed-identity-module, .global-nav__me-photo", timeout=5000)
    except PlaywrightTimeout:
        pass  # User can log in manually when headless=False; session_manager saves state after.

async def search_jobs(page: Page, keywords: list[str], location: str | None = None, job_type: str | None = None, min_salary: int | None = None) -> list[dict]:
    """Returns a list of {title, company, url} dicts for matching listings."""
    jobs: list[dict] = []
    
    # We'll just search the first keyword for simplicity, or loop. Let's use the first one.
    if not keywords:
        return jobs
        
    keyword = keywords[0]
    
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}"
    if location:
        search_url += f"&location={location.replace(' ', '%20')}"
        
    await page.goto(search_url)
    try:
        await page.wait_for_selector(".jobs-search-results-list", timeout=10_000)
    except PlaywrightTimeout:
        return jobs  # No results or page failed to load

    # Extract job cards
    cards = await page.query_selector_all(".job-card-container")
    for card in cards:
        title_el = await card.query_selector(".job-card-list__title, .artdeco-entity-lockup__title")
        company_el = await card.query_selector(".job-card-container__company-name, .artdeco-entity-lockup__subtitle")
        link_el = await card.query_selector("a.job-card-container__link, a.job-card-list__title")
        
        if title_el and link_el:
            title = await title_el.inner_text()
            company = await company_el.inner_text() if company_el else "Unknown"
            href = await link_el.get_attribute("href")
            if href:
                url = href.split("?")[0]
                if not url.startswith("http"):
                    url = "https://www.linkedin.com" + url
                jobs.append({"title": title.strip(), "company": company.strip(), "url": url})
                
    return jobs


async def open_application_modal(page: Page, job: dict) -> None:
    await page.goto(job["url"])
    try:
        # Wait for the Easy Apply button
        btn = await page.wait_for_selector("button.jobs-apply-button", timeout=5000)
        if btn:
            await btn.click()
            await page.wait_for_selector(".jobs-easy-apply-modal", timeout=5000)
    except PlaywrightTimeout:
        pass


async def read_form_fields(page: Page) -> list[dict]:
    """Returns [{label, type, selector}, ...] for the current modal step."""
    fields = []
    # Try to find all visible inputs in the modal
    form_groups = await page.query_selector_all(".jobs-easy-apply-form-section__grouping, .fb-dash-form-element")
    for group in form_groups:
        label_el = await group.query_selector("label")
        input_el = await group.query_selector("input, select, textarea")
        
        if label_el and input_el:
            label_text = await label_el.inner_text()
            tag_name = await input_el.evaluate("el => el.tagName.toLowerCase()")
            input_type = await input_el.get_attribute("type")
            
            field_type = "text"
            if tag_name == "select":
                field_type = "select"
            elif input_type in ["radio", "checkbox", "file"]:
                field_type = input_type
                
            selector = await input_el.evaluate(
                "el => el.id ? '#' + el.id : el.tagName.toLowerCase() + '[name=\"' + el.name + '\"]'"
            )
            
            fields.append({
                "label": label_text.strip(),
                "type": field_type,
                "selector": selector
            })
    return fields


async def fill_field(page: Page, field: dict, value: str) -> None:
    selector = field["selector"]
    field_type = field["type"]
    
    try:
        if field_type == "text":
            await page.fill(selector, value)
        elif field_type == "select":
            await page.select_option(selector, label=value)
        elif field_type == "radio" or field_type == "checkbox":
            if str(value).lower() in ["yes", "true", "1"]:
                await page.check(selector)
        elif field_type == "file":
            await page.set_input_files(selector, value)
    except Exception:
        pass # Log error in real implementation


async def submit(page: Page) -> None:
    try:
        # Click next or submit button
        btn = await page.query_selector("button[aria-label='Submit application'], button[aria-label='Review your application'], button[aria-label='Continue to next step']")
        if btn:
            await btn.click()
            await page.wait_for_timeout(2000) # Wait for transition
    except Exception:
        pass
