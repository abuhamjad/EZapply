from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Application
from app.schemas.api import (
    AnalyticsOut,
    ApplicationDataPoint,
    DashboardOut,
    DashboardStats,
    FunnelItem,
    PlatformDataPoint,
)

FUNNEL_COLORS = {
    "Applied": "#10b981",
    "Viewed": "#3b82f6",
    "Responded": "#f59e0b",
    "Interview": "#8b5cf6",
}


def _status_counts(db: Session) -> dict[str, int]:
    rows = (
        db.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )
    return {status: count for status, count in rows}


def get_dashboard(db: Session) -> DashboardOut:
    counts = _status_counts(db)
    total = db.query(func.count(Application.id)).scalar() or 0
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    applied_today = (
        db.query(func.count(Application.id))
        .filter(Application.applied_at >= today_start)
        .scalar()
        or 0
    )
    viewed = counts.get("viewed", 0) + counts.get("responded", 0) + counts.get("interview", 0)
    responses = counts.get("responded", 0) + counts.get("interview", 0)
    interviews = counts.get("interview", 0)

    funnel = [
        FunnelItem(name="Applied", value=total, color=FUNNEL_COLORS["Applied"]),
        FunnelItem(name="Viewed", value=viewed, color=FUNNEL_COLORS["Viewed"]),
        FunnelItem(name="Responded", value=responses, color=FUNNEL_COLORS["Responded"]),
        FunnelItem(name="Interview", value=interviews, color=FUNNEL_COLORS["Interview"]),
    ]

    recent = (
        db.query(Application)
        .order_by(Application.applied_at.desc())
        .limit(5)
        .all()
    )

    return DashboardOut(
        stats=DashboardStats(
            total_applied=total,
            applied_today=applied_today,
            viewed=viewed,
            responses=responses,
            interviews=interviews,
        ),
        funnel=funnel,
        recent_activity=recent,
    )


def get_analytics(db: Session) -> AnalyticsOut:
    now = datetime.utcnow()
    week_start = (now - timedelta(days=6)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    apps = db.query(Application).filter(Application.applied_at >= week_start).all()
    days: list[ApplicationDataPoint] = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_end = day + timedelta(days=1)
        day_apps = [a for a in apps if day <= a.applied_at < day_end]
        days.append(
            ApplicationDataPoint(
                day=day.strftime("%a"),
                sent=len(day_apps),
                responses=len(
                    [a for a in day_apps if a.status in ("responded", "interview")]
                ),
            )
        )

    platform_rows = (
        db.query(Application.platform, func.count(Application.id))
        .group_by(Application.platform)
        .all()
    )
    response_rows = (
        db.query(Application.platform, func.count(Application.id))
        .filter(Application.status.in_(["responded", "interview"]))
        .group_by(Application.platform)
        .all()
    )
    responses_by_platform = {p: c for p, c in response_rows}
    platforms = [
        PlatformDataPoint(
            platform=p,
            applied=c,
            responses=responses_by_platform.get(p, 0),
        )
        for p, c in platform_rows
    ]

    return AnalyticsOut(application_data=days, platform_data=platforms)
