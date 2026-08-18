"""
LinkedIn-specific platform adapter for automated job applications.
Handles: login detection, job search (Easy Apply filter), modal navigation
(multi-step), field reading, filling, and final submission.
"""
import asyncio
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeout
from app.core.logging import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────────────────────

async def ensure_logged_in(
    page: Page, timeout_seconds: int = 60, on_timeout_callback=None
) -> bool:
    """
    Navigate to LinkedIn login and wait for the user to sign in.
    Returns True when login is detected, False on timeout.
    """
    logger.info("Navigating to LinkedIn login page...")
    try:
        await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
    except Exception as e:
        logger.debug("Initial goto error (continuing): %s", e)

    start_time = asyncio.get_event_loop().time()
    check_interval = 1.5
    logged_in_paths = ["/feed", "/jobs", "/mynetwork", "/messaging", "/in/", "/home"]
    logged_in_selectors = [
        ".global-nav__me-photo",
        "#global-nav-search",
        ".global-nav",
        "nav.global-nav",
        ".profile-rail-card",
        "img.global-nav__me-photo",
        ".feed-identity-module",
    ]

    while asyncio.get_event_loop().time() - start_time < timeout_seconds:
        try:
            current_url = page.url.lower()

            if any(path in current_url for path in logged_in_paths):
                logger.info("LinkedIn login detected via URL: %s", current_url)
                return True

            for selector in logged_in_selectors:
                el = await page.query_selector(selector)
                if el:
                    logger.info("LinkedIn login detected via selector '%s'", selector)
                    return True
        except Exception:
            pass

        if on_timeout_callback:
            elapsed = asyncio.get_event_loop().time() - start_time
            try:
                await on_timeout_callback(int(max(0, timeout_seconds - elapsed)))
            except Exception:
                pass

        await asyncio.sleep(check_interval)

    logger.warning("LinkedIn login buffer timed out after %s seconds", timeout_seconds)
    return False


# ─────────────────────────────────────────────────────────────────────────────
# JOB SEARCH
# ─────────────────────────────────────────────────────────────────────────────

async def search_jobs(
    page: Page,
    keywords: list[str],
    location: str | None = None,
    job_type: str | None = None,
    min_salary: int | None = None,
) -> list[dict]:
    """Returns a list of {title, company, url} dicts for Easy Apply listings."""
    jobs: list[dict] = []
    if not keywords:
        return jobs

    for keyword in keywords:
        found = await _search_keyword(page, keyword, location)
        for job in found:
            if not any(j["url"] == job["url"] for j in jobs):
                jobs.append(job)

    logger.info("Total LinkedIn Easy Apply listings found: %d", len(jobs))
    return jobs


async def _search_keyword(page: Page, keyword: str, location: str | None) -> list[dict]:
    """Search LinkedIn jobs for a single keyword and return parsed listings."""
    jobs: list[dict] = []

    search_url = (
        f"https://www.linkedin.com/jobs/search/"
        f"?keywords={keyword.replace(' ', '%20')}&f_AL=true"
    )
    if location:
        search_url += f"&location={location.replace(' ', '%20')}"

    logger.info("LinkedIn job search URL: %s", search_url)

    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=20_000)
    except Exception as e:
        logger.warning("Failed to navigate to search URL: %s", e)
        return jobs

    # Wait for results container
    try:
        await page.wait_for_selector(
            ".jobs-search-results-list, .scaffold-layout__list, ul.jobs-search__results-list, .job-card-container",
            timeout=12_000,
        )
    except PlaywrightTimeout:
        logger.info("Job search results container timeout — scanning existing DOM")

    # Scroll to trigger lazy-loading
    try:
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 600)")
            await asyncio.sleep(0.8)
    except Exception:
        pass

    # Try multiple card selectors in order of specificity
    card_selectors = [
        ".job-card-container",
        "li.jobs-search-results__list-item",
        ".jobs-search-results-list li",
        "div[data-job-id]",
    ]
    cards = []
    for sel in card_selectors:
        found = await page.query_selector_all(sel)
        if found:
            cards = found
            logger.debug("Using card selector '%s', found %d cards", sel, len(found))
            break

    for card in cards:
        try:
            # Title: prefer the <strong> inside the anchor; fall back to anchor text
            title = None
            title_selectors = [
                "a.job-card-list__title--link strong",
                "a.job-card-container__link strong",
                ".job-card-list__title strong",
                ".artdeco-entity-lockup__title strong",
                "a.job-card-list__title",
                "a.job-card-container__link",
                ".job-card-list__title",
            ]
            for ts in title_selectors:
                el = await card.query_selector(ts)
                if el:
                    title = (await el.inner_text()).strip()
                    if title:
                        break

            # Company name
            company = "Unknown Company"
            company_selectors = [
                ".job-card-container__company-name",
                ".artdeco-entity-lockup__subtitle",
                ".job-card-container__primary-description",
                "span.job-card-container__company-name",
            ]
            for cs in company_selectors:
                el = await card.query_selector(cs)
                if el:
                    company = (await el.inner_text()).strip()
                    if company:
                        break

            # URL
            link_el = await card.query_selector(
                "a.job-card-list__title--link, a.job-card-container__link, a.job-card-list__title"
            )
            if not title or not link_el:
                continue

            href = await link_el.get_attribute("href")
            if not href:
                continue

            url = href.split("?")[0]
            if not url.startswith("http"):
                url = "https://www.linkedin.com" + url

            jobs.append({"title": title, "company": company, "url": url})

        except Exception as e:
            logger.debug("Error parsing job card: %s", e)

    logger.info("Extracted %d listings for keyword '%s'", len(jobs), keyword)
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION MODAL
# ─────────────────────────────────────────────────────────────────────────────

async def open_application_modal(page: Page, job: dict) -> bool:
    """Navigate to the job URL and click the Easy Apply button."""
    logger.info("Opening '%s' at '%s'", job.get("title"), job.get("company"))
    try:
        await page.goto(job["url"], wait_until="domcontentloaded", timeout=20_000)
    except Exception as e:
        logger.debug("Failed to load job URL %s: %s", job.get("url"), e)
        return False

    # Wait for job detail panel to load
    try:
        await page.wait_for_selector(".jobs-details, .job-view-layout", timeout=8_000)
    except PlaywrightTimeout:
        pass

    btn_selectors = [
        "button.jobs-apply-button",
        "button[aria-label*='Easy Apply']",
        ".jobs-apply-button--top-card button",
        "button.jobs-apply-button--top-card",
        "button:has-text('Easy Apply')",
    ]
    for sel in btn_selectors:
        try:
            btn = await page.query_selector(sel)
            if btn and await btn.is_visible():
                await btn.click()
                await page.wait_for_selector(
                    ".jobs-easy-apply-modal, div[role='dialog']", timeout=6_000
                )
                logger.info("Easy Apply modal opened for '%s'", job.get("title"))
                return True
        except Exception:
            continue

    logger.info("No Easy Apply button found for '%s'", job.get("title"))
    return False


# ─────────────────────────────────────────────────────────────────────────────
# FORM FIELD READING
# ─────────────────────────────────────────────────────────────────────────────

async def read_form_fields(page: Page) -> list[dict]:
    """
    Returns [{label, type, selector}, ...] for all visible inputs in the current
    modal step. Handles text, select, radio, checkbox, file, and textarea.
    """
    fields: list[dict] = []

    group_selectors = [
        ".jobs-easy-apply-form-section__grouping",
        ".fb-dash-form-element",
        ".jobs-easy-apply-modal .artdeco-text-input--container",
        ".jobs-easy-apply-content .artdeco-text-input--container",
    ]

    groups = []
    for gs in group_selectors:
        groups = await page.query_selector_all(gs)
        if groups:
            break

    for group in groups:
        try:
            label_el = await group.query_selector("label, legend, span.t-14.t-bold")
            input_el = await group.query_selector("input:not([type='hidden']), select, textarea")

            if not input_el:
                continue

            label_text = ""
            if label_el:
                label_text = (await label_el.inner_text()).strip()

            tag_name: str = await input_el.evaluate("el => el.tagName.toLowerCase()")
            input_type: str = await input_el.get_attribute("type") or ""

            if tag_name == "select":
                field_type = "select"
            elif input_type in ["radio", "checkbox", "file"]:
                field_type = input_type
            elif tag_name == "textarea":
                field_type = "text"
            else:
                field_type = "text"

            # Build a reliable CSS selector using id or name
            selector: str = await input_el.evaluate(
                "el => el.id ? '#' + el.id : "
                "el.tagName.toLowerCase() + (el.name ? '[name=\"' + el.name + '\"]' : '')"
            )

            if label_text:
                fields.append({
                    "label": label_text,
                    "type": field_type,
                    "selector": selector,
                })
        except Exception as e:
            logger.debug("Error reading form group: %s", e)

    return fields


# ─────────────────────────────────────────────────────────────────────────────
# FIELD FILLING
# ─────────────────────────────────────────────────────────────────────────────

async def fill_field(page: Page, field: dict, value: str) -> None:
    """Fill a single form field by its type."""
    selector = field["selector"]
    field_type = field["type"]

    try:
        if field_type == "text":
            await page.fill(selector, str(value))
        elif field_type == "select":
            try:
                await page.select_option(selector, label=str(value))
            except Exception:
                # Try selecting by partial match
                await page.select_option(selector, value=str(value))
        elif field_type in ["radio", "checkbox"]:
            if str(value).lower() in ["yes", "true", "1", "agreed"]:
                await page.check(selector)
        elif field_type == "file":
            await page.set_input_files(selector, value)
    except Exception as e:
        logger.debug("Failed filling '%s' (%s) with '%s': %s", field.get("label"), field_type, value, e)


# ─────────────────────────────────────────────────────────────────────────────
# MULTI-STEP SUBMISSION
# ─────────────────────────────────────────────────────────────────────────────

async def submit(page: Page) -> None:
    """
    Navigate through all steps of the LinkedIn Easy Apply modal:
      Next → Next → … → Review → Submit application
    Dismisses overlay popups before each step and post-submit dialogs after.
    """
    MAX_STEPS = 15  # safety cap

    for step in range(MAX_STEPS):
        await asyncio.sleep(1.5)  # let DOM settle

        # Always dismiss any overlay popups before acting
        await _dismiss_overlay_popups(page)
        await asyncio.sleep(0.5)

        # If modal closed, we're done
        modal = await page.query_selector(".jobs-easy-apply-modal, div[role='dialog']")
        if not modal:
            logger.info("Modal closed — submission complete at step %d", step)
            return

        # Ordered priority: Submit first, then Review, then Next/Continue
        # Each entry: (action_label, list_of_selectors_to_try)
        step_actions = [
            ("submit", [
                "button[aria-label='Submit application']",
                "button:has-text('Submit application')",
                "footer button.artdeco-button--primary[aria-label*='Submit']",
            ]),
            ("review", [
                "button[aria-label='Review your application']",
                "button:has-text('Review')",
            ]),
            ("continue", [
                "button[aria-label='Continue to next step']",
                "button:has-text('Continue to next step')",
            ]),
            ("next", [
                "footer button.artdeco-button--primary",
                ".jobs-easy-apply-modal footer button.artdeco-button--primary",
                "button[data-easy-apply-next-button]",
                "button:has-text('Next')",
            ]),
        ]

        clicked = False
        for action_label, selectors in step_actions:
            for sel in selectors:
                try:
                    btn = await page.query_selector(sel)
                    if btn and await btn.is_visible() and await btn.is_enabled():
                        logger.info("Step %d: clicking '%s' (%s)", step, action_label, sel)
                        await btn.click()
                        clicked = True

                        if action_label == "submit":
                            await asyncio.sleep(2)
                            await _dismiss_post_submit_dialogs(page)
                            return
                        break
                except Exception:
                    continue
            if clicked:
                break

        if not clicked:
            logger.warning("Step %d: no actionable button found — aborting", step)
            return

    logger.warning("Exceeded MAX_STEPS (%d) — aborting submit loop", MAX_STEPS)


async def _dismiss_overlay_popups(page: Page) -> None:
    """
    Dismiss any non-modal overlays that may block button clicks:
    - LinkedIn Premium upsell tooltip
    - AI Tailor tooltip
    - Any dismissable overlay with an X button inside the modal
    """
    popup_dismiss_selectors = [
        # Premium/AI tooltip close button (dark overlay inside modal)
        ".premium-upsell-link__tooltip button",
        "div.jobs-easy-apply-modal button[aria-label='Dismiss']",
        # Generic close buttons on tooltips/overlays
        "button[aria-label='Close']",
        "button.msg-overlay-bubble-header__control[aria-label='Close']",
        # The × button on the AI Tailor / Premium dark card
        ".jobs-premium-applicant-insights__dismiss-btn",
        "button.artdeco-toast-item__dismiss",
        # Any visible 'x' inside a tooltip-like popup that's NOT the main modal header
        ".artdeco-inline-feedback button",
    ]

    for sel in popup_dismiss_selectors:
        try:
            btns = await page.query_selector_all(sel)
            for btn in btns:
                if await btn.is_visible():
                    await btn.click()
                    logger.debug("Dismissed overlay popup via '%s'", sel)
                    await asyncio.sleep(0.3)
        except Exception:
            continue

    # Close the Premium tooltip by pressing Escape if still visible
    try:
        premium = await page.query_selector(".premium-upsell-link__tooltip, .jobs-premium-upsell-card")
        if premium and await premium.is_visible():
            await page.keyboard.press("Escape")
            await asyncio.sleep(0.3)
    except Exception:
        pass


async def _dismiss_post_submit_dialogs(page: Page) -> None:
    """Close the 'Application submitted' or follow-up dialog after submission."""
    dismiss_selectors = [
        "button[aria-label='Dismiss']",
        "button[data-control-name='post_apply_followup_dismiss']",
        "button:has-text('Not now')",
        "button:has-text('Done')",
        "button:has-text('Dismiss')",
    ]
    for sel in dismiss_selectors:
        try:
            btn = await page.query_selector(sel)
            if btn and await btn.is_visible():
                await btn.click()
                logger.info("Dismissed post-submit dialog via '%s'", sel)
                await asyncio.sleep(0.5)
                return
        except Exception:
            continue

