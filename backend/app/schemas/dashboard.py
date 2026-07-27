from datetime import datetime
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_applied: int = 0
    applied_today: int = 0
    viewed: int = 0
    responses: int = 0
    interviews: int = 0


class FunnelItem(BaseModel):
    name: str
    value: int
    color: str


class RecentActivityItem(BaseModel):
    id: str | int
    role: str
    company: str
    platform: str
    status: str
    applied_at: str


class DashboardResponse(BaseModel):
    stats: DashboardStats
    funnel: list[FunnelItem]
    recent_activity: list[RecentActivityItem]
