from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company: str
    role: str
    platform: str
    status: str
    job_url: str | None = None
    applied_at: datetime


class StatsSummaryResponse(BaseModel):
    total_applications: int
    success_rate: float
    daily_breakdown: dict[str, int]  # "YYYY-MM-DD" -> count
    recent: list[ApplicationResponse]
