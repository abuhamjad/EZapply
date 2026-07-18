from pydantic import BaseModel
from typing import List


class ApplicationDataPoint(BaseModel):
    day: str
    sent: int
    responses: int


class PlatformDataPoint(BaseModel):
    platform: str
    applied: int
    responses: int


class ApplicationsResponse(BaseModel):
    data: List[ApplicationDataPoint]


class PlatformsResponse(BaseModel):
    data: List[PlatformDataPoint]


class AnalyticsSummaryResponse(BaseModel):
    this_week: int
    avg_per_day: float
    response_rate: float
    interview_rate: float
