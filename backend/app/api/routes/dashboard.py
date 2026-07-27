from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardStats,
    FunnelItem,
    RecentActivityItem,
)
from app.services.stats import StatsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    summary = await StatsService(db).get_summary()

    recent_items = [
        RecentActivityItem(
            id=item.id,
            role=item.role,
            company=item.company,
            platform=item.platform,
            status=item.status,
            applied_at=item.applied_at.isoformat() if hasattr(item.applied_at, "isoformat") else str(item.applied_at),
        )
        for item in summary["recent"]
    ]

    total_applied = summary["total_applications"]
    applied_today = len([x for x in summary["recent"] if x.status == "APPLIED"])

    return DashboardResponse(
        stats=DashboardStats(
            total_applied=total_applied,
            applied_today=applied_today,
            viewed=summary["viewed"],
            responses=summary["responses"],
            interviews=summary["interviews"],
        ),
        funnel=[
            FunnelItem(name="Applied", value=total_applied, color="#3B82F6"),
            FunnelItem(name="Viewed", value=summary["viewed"], color="#8B5CF6"),
            FunnelItem(name="Responses", value=summary["responses"], color="#10B981"),
            FunnelItem(name="Interviews", value=summary["interviews"], color="#F59E0B"),
        ],
        recent_activity=recent_items,
    )
