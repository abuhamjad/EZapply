from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ApplicationStatus
from app.repositories.application_repository import ApplicationRepository
from app.schemas.application import ApplicationResponse, StatsSummaryResponse


class StatsService:
    def __init__(self, db: AsyncSession):
        self.repo = ApplicationRepository(db)

    async def get_summary(self) -> dict:
        total = await self.repo.count_all()
        status_counts = await self.repo.group_by_status()
        
        applied = status_counts.get("APPLIED", 0)
        viewed = status_counts.get("VIEWED", 0)
        responses = status_counts.get("RESPONDED", 0)
        interviews = status_counts.get("INTERVIEW", 0)
        
        daily = await self.repo.daily_breakdown_full()
        recent_rows = await self.repo.list_recent(limit=20)
        platform_data = await self.repo.platform_breakdown()

        return {
            "total_applications": total,
            "applied": applied,
            "viewed": viewed,
            "responses": responses,
            "interviews": interviews,
            "daily_breakdown": daily,
            "platform_breakdown": platform_data,
            "recent": [ApplicationResponse.model_validate(r) for r in recent_rows],
        }
