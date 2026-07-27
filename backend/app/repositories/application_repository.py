from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application


class ApplicationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, application: Application) -> Application:
        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)
        return application

    async def list_recent(self, limit: int = 20) -> list[Application]:
        result = await self.db.execute(
            select(Application).order_by(Application.applied_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def count_all(self) -> int:
        result = await self.db.execute(select(func.count(Application.id)))
        return result.scalar_one()

    async def count_by_status(self, status: str) -> int:
        result = await self.db.execute(
            select(func.count(Application.id)).where(Application.status == status)
        )
        return result.scalar_one()

    async def group_by_status(self) -> dict[str, int]:
        result = await self.db.execute(
            select(Application.status, func.count(Application.id))
            .group_by(Application.status)
        )
        return {status: count for status, count in result.all()}

    async def platform_breakdown(self) -> dict[str, dict[str, int]]:
        result = await self.db.execute(
            select(Application.platform, Application.status, func.count(Application.id))
            .group_by(Application.platform, Application.status)
        )
        data = {}
        for platform, status, count in result.all():
            if platform not in data:
                data[platform] = {"applied": 0, "responses": 0}
            if status == "APPLIED":
                data[platform]["applied"] += count
            elif status in ["VIEWED", "RESPONDED", "INTERVIEW"]:
                data[platform]["responses"] += count
                # Optional: responses means any positive signal
        return data

    async def daily_breakdown_full(self, days: int = 7) -> dict[str, dict[str, int]]:
        result = await self.db.execute(
            select(func.date(Application.applied_at), Application.status, func.count(Application.id))
            .group_by(func.date(Application.applied_at), Application.status)
            .order_by(func.date(Application.applied_at).desc())
        )
        data = {}
        for day, status, count in result.all():
            day_str = str(day)
            if day_str not in data:
                data[day_str] = {"sent": 0, "responses": 0}
            if status == "APPLIED":
                data[day_str]["sent"] += count
            elif status in ["VIEWED", "RESPONDED", "INTERVIEW"]:
                data[day_str]["responses"] += count
        return data

    async def daily_breakdown(self, days: int = 14) -> dict[str, int]:
        result = await self.db.execute(
            select(func.date(Application.applied_at), func.count(Application.id))
            .group_by(func.date(Application.applied_at))
            .order_by(func.date(Application.applied_at).desc())
            .limit(days)
        )
        return {str(day): count for day, count in result.all()}
