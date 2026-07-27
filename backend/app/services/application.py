from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ApplicationStatus
from app.models.application import Application
from app.repositories.application_repository import ApplicationRepository


class ApplicationTrackingService:
    """Called by the automation engine right after a form submit succeeds/fails."""

    def __init__(self, db: AsyncSession):
        self.repo = ApplicationRepository(db)

    async def create_application(
        self,
        *,
        bot_run_id: str,
        company: str,
        role: str,
        platform: str,
        job_url: str | None = None,
        status: ApplicationStatus = ApplicationStatus.APPLIED,
    ) -> Application:
        application = Application(
            bot_run_id=bot_run_id,
            company=company,
            role=role,
            platform=platform,
            job_url=job_url,
            status=status.value,
        )
        return await self.repo.create(application)
