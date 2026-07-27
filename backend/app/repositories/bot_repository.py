from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bot import BotRun


class BotRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, run: BotRun) -> BotRun:
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get(self, run_id: str) -> BotRun | None:
        result = await self.db.execute(select(BotRun).where(BotRun.id == run_id))
        return result.scalar_one_or_none()

    async def update(self, run: BotRun, **fields) -> BotRun:
        for key, value in fields.items():
            setattr(run, key, value)
        await self.db.commit()
        await self.db.refresh(run)
        return run
