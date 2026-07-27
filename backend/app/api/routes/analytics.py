from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.schemas.analytics import (
    AnalyticsResponse,
    ApplicationDataPoint,
    PlatformDataPoint,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(db: AsyncSession = Depends(get_db)):
    from app.services.stats import StatsService
    summary = await StatsService(db).get_summary()
    
    app_data = []
    for day_str, counts in summary["daily_breakdown"].items():
        app_data.append(ApplicationDataPoint(
            day=day_str[-5:],  # MM-DD
            sent=counts["sent"],
            responses=counts["responses"],
        ))
    
    plat_data = []
    for platform, counts in summary["platform_breakdown"].items():
        plat_data.append(PlatformDataPoint(
            platform=platform,
            applied=counts["applied"],
            responses=counts["responses"],
        ))

    return AnalyticsResponse(
        application_data=app_data,
        platform_data=plat_data,
    )
