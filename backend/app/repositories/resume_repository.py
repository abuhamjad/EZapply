from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume


class ResumeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, resume: Resume) -> Resume:
        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)
        return resume

    async def get(self, resume_id: str) -> Resume | None:
        result = await self.db.execute(select(Resume).where(Resume.id == resume_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Resume]:
        result = await self.db.execute(select(Resume).order_by(Resume.created_at.desc()))
        return list(result.scalars().all())

    async def set_default(self, resume_id: str) -> None:
        await self.db.execute(update(Resume).values(is_default=False))
        await self.db.execute(update(Resume).where(Resume.id == resume_id).values(is_default=True))
        await self.db.commit()

    async def get_default(self) -> Resume | None:
        result = await self.db.execute(select(Resume).where(Resume.is_default.is_(True)))
        return result.scalar_one_or_none()
