"""
Core Playwright runner. This is invoked as a background asyncio task by
BotService.start_run() (and again by BotService.resume_run() after a
paused question is answered). It owns the full lifecycle of one BotRun:

  1. Open a browser session (via SessionManager)
  2. For each platform -> search jobs -> for each job -> open modal -> fill & submit
  3. On an unmapped field: pause the run, record a ScreeningQuestion, persist
     a resume_context (platform + job + keyword index) and return control.
     The run resumes later via BotService.resume_run(), which re-invokes this
     function; it fast-forwards past already-completed platforms/jobs using
     that resume_context, then re-opens the same job so the field that was
     unknown last time now resolves via the freshly-learned answer.
  4. On submit: write an Application record via ApplicationTrackingService

NOTE: Automating applications on third-party sites (LinkedIn, Indeed, etc.)
may violate those platforms' Terms of Service, independent of anything
technical here — worth checking before running this against real accounts.

This file intentionally stays thin: platform-specific selectors/logic live
in automation/platforms/*.py so engine.py never branches on "if linkedin".
"""
import json
from datetime import datetime, timezone

from app.automation.form_filler import FormFiller
from app.automation.platforms import indeed, linkedin
from app.automation.session_manager import PlatformSessionManager
from app.core.constants import BotRunStatus, Platform
from app.core.logging import get_logger
from app.database.connection import AsyncSessionLocal
from app.repositories.bot_repository import BotRepository
from app.services.application import ApplicationTrackingService
from app.core.constants import ApplicationStatus

logger = get_logger(__name__)

PLATFORM_ADAPTERS = {
    Platform.LINKEDIN.value: linkedin,
    Platform.INDEED.value: indeed,
}


async def run_automation(bot_run_id: str) -> None:
    """
    Entry point launched via `asyncio.create_task`. Owns its own DB session
    since it runs outside the request/response cycle.
    """
    async with AsyncSessionLocal() as db:
        repo = BotRepository(db)
        run = None

        try:
            run = await repo.get(bot_run_id)
            if run is None:
                logger.error("BotRun %s not found, aborting", bot_run_id)
                return

            platforms = json.loads(run.platforms_json)
            keywords = json.loads(run.keywords_json)

            # If we're resuming a previously-paused run, figure out where to
            # fast-forward to. Otherwise start from the very beginning.
            resume_ctx = json.loads(run.resume_context_json) if run.resume_context_json else None

            run = await repo.update(run, status=BotRunStatus.RUNNING.value)

            session_manager = PlatformSessionManager()
            form_filler = FormFiller(db=db, bot_run_id=bot_run_id)
            tracking_service = ApplicationTrackingService(db)

            async with session_manager.browser_session() as browser:
                for platform_name in platforms:
                    # Skip platforms that already finished in a prior pass.
                    if resume_ctx and platform_name != resume_ctx["platform"]:
                        continue

                    adapter = PLATFORM_ADAPTERS.get(platform_name)
                    if adapter is None:
                        logger.warning("No adapter for platform: %s", platform_name)
                        continue

                    page = await session_manager.get_authenticated_page(browser, platform_name)

                    job_listings = await adapter.search_jobs(page, keywords=keywords)

                    # Fast-forward to the job we paused on, if resuming.
                    if resume_ctx and platform_name == resume_ctx["platform"]:
                        job_listings = _fast_forward(job_listings, resume_ctx["job_url"])
                        resume_ctx = None  # only applies once, to the first matching platform

                    for job in job_listings:
                        if run.applications_submitted >= run.application_limit:
                            break

                        await adapter.open_application_modal(page, job)
                        outcome = await form_filler.fill_and_submit(page, adapter, job)

                        if outcome == "paused":
                            await repo.update(
                                run,
                                status=BotRunStatus.PAUSED_NEEDS_INPUT.value,
                                resume_context_json=json.dumps(
                                    {"platform": platform_name, "job_url": job.get("url")}
                                ),
                            )
                            return  # Wait for POST /bot/resolve-question to resume

                        if outcome == "submitted":
                            await tracking_service.create_application(
                                bot_run_id=run.id,
                                company=job.get("company", "Unknown"),
                                role=job.get("title", "Unknown"),
                                platform=platform_name,
                                job_url=job.get("url"),
                                status=ApplicationStatus.APPLIED,
                            )
                            run = await repo.update(
                                run, applications_submitted=run.applications_submitted + 1
                            )

            await repo.update(
                run,
                status=BotRunStatus.COMPLETED.value,
                finished_at=datetime.now(timezone.utc),
                resume_context_json=None,
            )

        except Exception as exc:  # noqa: BLE001
            logger.exception("Automation run %s failed", bot_run_id)
            if "Executable doesn't exist" in str(exc):
                logger.error(
                    "Playwright browser executable is missing for run %s. "
                    "Run `playwright install chromium` in this environment.",
                    bot_run_id,
                )
            if run is not None:
                await repo.update(run, status=BotRunStatus.FAILED.value, error_message=str(exc))


def _fast_forward(job_listings: list[dict], job_url: str | None) -> list[dict]:
    """Return job_listings starting at (and including) the job matching job_url."""
    if not job_url:
        return job_listings
    for i, job in enumerate(job_listings):
        if job.get("url") == job_url:
            return job_listings[i:]
    # Job no longer in results (e.g. listing expired) — nothing to resume onto.
    return []
