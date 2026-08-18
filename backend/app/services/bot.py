import json
import asyncio
import threading
import sys
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BotRunStatus
from app.core.logging import get_logger
from app.models.bot import BotConfig, BotRun
from app.repositories.bot_repository import BotRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.bot import BotStartRequest, BotStartResponse, BotStatusResponse, ScreeningQuestionResponse

logger = get_logger(__name__)

# Registry of active event loops running automation in worker threads
_active_loops: dict[str, asyncio.AbstractEventLoop] = {}


def _spawn_bot_task(run_id: str) -> threading.Thread:
    """Spawns automation execution inside a dedicated thread with a ProactorEventLoop on Windows."""
    def runner():
        if sys.platform == "win32":
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        _active_loops[run_id] = loop
        try:
            from app.automation.engine import run_automation
            loop.run_until_complete(run_automation(run_id))
        except asyncio.CancelledError:
            logger.info("Automation loop cancelled for run %s", run_id)
        except Exception as e:
            logger.exception("Automation failed for run %s: %s", run_id, e)
        finally:
            _active_loops.pop(run_id, None)
            try:
                loop.close()
            except Exception:
                pass

    t = threading.Thread(target=runner, name=f"bot-worker-{run_id}", daemon=True)
    t.start()
    return t


def _cancel_bot_task(run_id: str) -> None:
    """Cancels running automation tasks in the worker loop."""
    loop = _active_loops.pop(run_id, None)
    if loop and loop.is_running():
        try:
            for task in asyncio.all_tasks(loop):
                loop.call_soon_threadsafe(task.cancel)
        except Exception as e:
            logger.debug("Error cancelling loop tasks for %s: %s", run_id, e)


class BotService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BotRepository(db)

    async def _sync_config_status(self, status: str) -> None:
        result = await self.db.execute(select(BotConfig).where(BotConfig.id == "default"))
        row = result.scalar_one_or_none()
        if row:
            row.status = status
            await self.db.commit()

    async def start_run(self, payload: BotStartRequest) -> BotStartResponse:
        # Domain rule: profile must be minimally complete before a run can start.
        from app.services.saved_info import SavedInfoService

        if not await SavedInfoService(self.db).is_profile_complete():
            raise ValueError("Saved info is incomplete (need full name, email, phone) before starting a run.")

        # Cancel any existing running tasks
        for active_id in list(_active_loops.keys()):
            _cancel_bot_task(active_id)

        run = BotRun(
            status=BotRunStatus.STARTED.value,
            platforms_json=json.dumps([p.value for p in payload.platforms]),
            keywords_json=json.dumps(payload.keywords),
            application_limit=payload.application_limit,
            resume_id=payload.resume_id,
        )
        run = await self.repo.create(run)
        await self._sync_config_status("running")

        _spawn_bot_task(run.id)

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

    async def pause_run(self, run_id: str) -> BotStatusResponse:
        run = await self.repo.get(run_id)
        if run is None:
            raise ValueError(f"Bot run {run_id} not found")

        _cancel_bot_task(run_id)

        run = await self.repo.update(run, status=BotRunStatus.PAUSED_NEEDS_INPUT.value)
        await self._sync_config_status("paused")
        return await self.get_status(run_id)

    async def resume_run(self, run_id: str) -> BotStatusResponse:
        run = await self.repo.get(run_id)
        if run is None:
            raise ValueError(f"Bot run {run_id} not found")

        # Stop any other active runs
        for active_id in list(_active_loops.keys()):
            if active_id != run_id:
                _cancel_bot_task(active_id)

        run = await self.repo.update(run, status=BotRunStatus.RUNNING.value)
        await self._sync_config_status("running")

        _spawn_bot_task(run_id)

        return await self.get_status(run_id)

    async def stop_run(self, run_id: str) -> BotStatusResponse:
        run = await self.repo.get(run_id)
        if run is None:
            raise ValueError(f"Bot run {run_id} not found")

        _cancel_bot_task(run_id)

        run = await self.repo.update(
            run,
            status=BotRunStatus.STOPPED.value,
            finished_at=datetime.now(timezone.utc),
        )
        await self._sync_config_status("stopped")
        return await self.get_status(run_id)
