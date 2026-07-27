from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_info import SavedInfo

SINGLETON_ID = 1  # single local user, single row


class SavedInfoRepository:
    """Pure DB access. No business logic here — that belongs in the service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self) -> SavedInfo | None:
        result = await self.db.execute(select(SavedInfo).where(SavedInfo.id == SINGLETON_ID))
        return result.scalar_one_or_none()

    async def get_or_create(self) -> SavedInfo:
        existing = await self.get()
        if existing:
            return existing
        row = SavedInfo(id=SINGLETON_ID)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def update(self, row: SavedInfo, **fields) -> SavedInfo:
        for key, value in fields.items():
            setattr(row, key, value)
        await self.db.commit()
        await self.db.refresh(row)
        return row
