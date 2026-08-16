from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import Platform


class BotConfigSchema(BaseModel):
    """Matches frontend BotConfig interface exactly."""
    linkedin: bool = True
    indeed: bool = True
    glassdoor: bool = False
    dice: bool = False
    job_type: str = "full-time"
    location: str = "Remote"
    min_salary: int = 80000
    apply_delay: int = 45


class BotStateSchema(BotConfigSchema):
    """Flat state: extends config fields + adds status."""
    status: str = "stopped"


class BotStatusUpdate(BaseModel):
    status: str


class BotStartRequest(BaseModel):
    platforms: list[Platform] = [Platform.LINKEDIN]
    keywords: list[str] = Field(default_factory=lambda: ["Frontend Developer"])
    application_limit: int = 25
    resume_id: str | None = None


class BotStartResponse(BaseModel):
    run_id: str
    status: str


class BotStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    applications_submitted: int
    error_message: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    pending_question: "ScreeningQuestionResponse | None" = None


class ScreeningQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question_text: str
    field_type: str
    job_title: str | None = None
    company: str | None = None


class ResolveQuestionRequest(BaseModel):
    question_id: str
    answer: str
    remember_for_future: bool = True