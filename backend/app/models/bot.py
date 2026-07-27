import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import BotRunStatus
from app.database.connection import Base


class BotConfig(Base):
    """Persistent bot configuration singleton (single row, id='default')."""
    __tablename__ = "bot_config"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="stopped")
    linkedin: Mapped[bool] = mapped_column(Boolean, default=True)
    indeed: Mapped[bool] = mapped_column(Boolean, default=True)
    glassdoor: Mapped[bool] = mapped_column(Boolean, default=False)
    dice: Mapped[bool] = mapped_column(Boolean, default=False)
    job_type: Mapped[str] = mapped_column(String(20), default="full-time")
    location: Mapped[str] = mapped_column(String(200), default="Remote")
    min_salary: Mapped[int] = mapped_column(Integer, default=80000)
    apply_delay: Mapped[int] = mapped_column(Integer, default=45)


class BotRun(Base):
    __tablename__ = "bot_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status: Mapped[str] = mapped_column(String(30), default=BotRunStatus.STARTED.value)

    platforms_json: Mapped[str] = mapped_column(Text)  # e.g. '["linkedin","indeed"]'
    keywords_json: Mapped[str] = mapped_column(Text)   # e.g. '["backend engineer"]'
    application_limit: Mapped[int] = mapped_column(Integer, default=25)
    resume_id: Mapped[str | None] = mapped_column(String(36))

    applications_submitted: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)

    # Where to pick back up after PAUSED_NEEDS_INPUT is resolved:
    # {"platform": "linkedin", "job_url": "...", "keyword_index": 2}
    resume_context_json: Mapped[str | None] = mapped_column(Text)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
