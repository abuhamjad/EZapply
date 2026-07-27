from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.schemas.application import StatsSummaryResponse
from app.services.stats import StatsService

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/summary", response_model=StatsSummaryResponse)
async def get_stats_summary(db: AsyncSession = Depends(get_db)):
    return await StatsService(db).get_summary()
