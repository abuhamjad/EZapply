from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


BotStatus = Literal["running", "paused", "stopped"]


class BotQuestion(BaseModel):
    field: str
    job: str = ""
    message: str


class BotStatusResponse(BaseModel):
    status: BotStatus
    run_id: int | None = None
    stats: dict[str, int] = Field(default_factory=dict)
    pending_question: BotQuestion | None = None
    updated_at: datetime | None = None


class BotStatusUpdateRequest(BaseModel):
    status: BotStatus


class BotConfigResponse(BaseModel):
    platforms: dict[str, bool]
    available_platforms: list[str]
    job_type: str = ""
    location: str = ""
    min_salary: str = ""
    apply_delay: int = 30
    keywords: list[str] = Field(default_factory=list)


class BotConfigUpdateRequest(BaseModel):
    platforms: dict[str, bool]
    job_type: str = ""
    location: str = ""
    min_salary: str = ""
    apply_delay: int = Field(default=30, ge=1, le=600)
    keywords: list[str] = Field(default_factory=list)


class StartAutomationRequest(BaseModel):
    config: BotConfigUpdateRequest | None = None


class BotResponseRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=4000)


class AutomationEventResponse(BaseModel):
    id: int | None = None
    run_id: int | None = None
    type: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
