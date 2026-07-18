from pydantic import BaseModel
from typing import List


class FunnelItem(BaseModel):
    name: str
    value: int
    color: str


class RecentActivityItem(BaseModel):
    id: int
    role: str
    company: str
    platform: str
    time: str
    status: str


class DashboardSummaryResponse(BaseModel):
    funnel_data: List[FunnelItem]
    recent_activity: List[RecentActivityItem]


class DashboardStatsResponse(BaseModel):
    total_applied: int
    viewed: int
    responses: int
    interviews: int
    applied_today: int
