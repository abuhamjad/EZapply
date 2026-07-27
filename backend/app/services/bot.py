import json
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BotRunStatus
from app.database.connection import AsyncSessionLocal
from app.core.logging import get_logger
from app.models.bot import BotRun
from app.repositories.bot_repository import BotRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.bot import BotStartRequest, BotStartResponse, BotStatusResponse, ScreeningQuestionResponse

logger = get_logger(__name__)


def _log_task_failure(task: asyncio.Task, run_id: str) -> None:
    try:
        exc = task.exception()
    except asyncio.CancelledError:
        logger.info("Automation task for run %s was cancelled", run_id)
        return
    except Exception:
        logger.exception("Could not inspect automation task for run %s", run_id)
        return

    if exc is None:
        return

    logger.error(
        "Automation task for run %s failed with an unhandled exception",
        run_id,
        exc_info=(type(exc), exc, exc.__traceback__),
    )


class BotService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BotRepository(db)

    async def start_run(self, payload: BotStartRequest) -> BotStartResponse:
        # Domain rule: profile must be minimally complete before a run can start.
        from app.services.saved_info import SavedInfoService

        if not await SavedInfoService(self.db).is_profile_complete():
            raise ValueError("Saved info is incomplete (need full name, email, phone) before starting a run.")

        run = BotRun(
            status=BotRunStatus.STARTED.value,
            platforms_json=json.dumps([p.value for p in payload.platforms]),
            keywords_json=json.dumps(payload.keywords),
            application_limit=payload.application_limit,
            resume_id=payload.resume_id,
        )
        run = await self.repo.create(run)

        # Fire-and-forget background task. In production, prefer a proper task
        # queue (arq / Celery) over asyncio.create_task so runs survive restarts.
        from app.automation.engine import run_automation

        task = asyncio.create_task(run_automation(run.id), name=f"bot-run-{run.id}")
        task.add_done_callback(lambda t, run_id=run.id: _log_task_failure(t, run_id))

        return BotStartResponse(run_id=run.id, status=run.status)

    async def get_status(self, run_id: str) -> BotStatusResponse:
        run = await self.repo.get(run_id)
        if run is None:
            raise ValueError(f"Bot run {run_id} not found")

        pending_question = None
        if run.status == BotRunStatus.PAUSED_NEEDS_INPUT.value:
            q_repo = QuestionRepository(self.db)
            question_row = await q_repo.get_latest_unresolved(run.id)
            if question_row is not None:
                pending_question = ScreeningQuestionResponse.model_validate(question_row)

        return BotStatusResponse(
            id=run.id,
            status=run.status,
            applications_submitted=run.applications_submitted,
            error_message=run.error_message,
            started_at=run.started_at,
            finished_at=run.finished_at,
            pending_question=pending_question,
        )

    async def resume_run(self, run_id: str) -> BotStatusResponse:
        run = await self.repo.get(run_id)
        if run is None:
            raise ValueError(f"Bot run {run_id} not found")
        if run.status != BotRunStatus.PAUSED_NEEDS_INPUT.value:
            raise ValueError(f"Bot run {run_id} is not paused (status={run.status})")

        import asyncio

        from app.automation.engine import run_automation

        asyncio.create_task(run_automation(run_id))
        return await self.get_status(run_id)

    async def stop_run(self, run_id: str) -> BotStatusResponse:
        run = await self.repo.get(run_id)
        if run is None:
            raise ValueError(f"Bot run {run_id} not found")
        from datetime import datetime, timezone

        run = await self.repo.update(run, status=BotRunStatus.STOPPED.value, finished_at=datetime.now(timezone.utc))
        return await self.get_status(run_id)
