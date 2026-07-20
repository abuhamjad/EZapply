from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    company: str
    platform: str
    status: str
    applied_at: datetime


class FunnelItem(BaseModel):
    name: str
    value: int
    color: str


class DashboardStats(BaseModel):
    total_applied: int
    applied_today: int
    viewed: int
    responses: int
    interviews: int


class DashboardOut(BaseModel):
    stats: DashboardStats
    funnel: list[FunnelItem]
    recent_activity: list[ApplicationOut]


class ApplicationDataPoint(BaseModel):
    day: str
    sent: int
    responses: int


class PlatformDataPoint(BaseModel):
    platform: str
    applied: int
    responses: int


class AnalyticsOut(BaseModel):
    application_data: list[ApplicationDataPoint]
    platform_data: list[PlatformDataPoint]


class KeywordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    kind: Literal["include", "exclude"]


class KeywordCreate(BaseModel):
    text: str
    kind: Literal["include", "exclude"] = "include"


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    last_edited: datetime


class TemplateCreate(BaseModel):
    name: str


class SavedInfoOut(BaseModel):
    saved_keywords: list[KeywordOut]
    excluded_keywords: list[KeywordOut]
    cover_letter_templates: list[TemplateOut]


class BotConfig(BaseModel):
    linkedin: bool = True
    indeed: bool = True
    glassdoor: bool = True
    dice: bool = False
    job_type: Literal["full-time", "contract", "part-time"] = "full-time"
    location: str = "Remote"
    min_salary: int = 80000
    apply_delay: int = 45


class BotStateOut(BotConfig):
    model_config = ConfigDict(from_attributes=True)

    status: Literal["running", "paused", "stopped"]


class BotStatusUpdate(BaseModel):
    status: Literal["running", "paused", "stopped"]
