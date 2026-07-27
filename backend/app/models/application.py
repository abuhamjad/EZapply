import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bot_run_id: Mapped[str | None] = mapped_column(String(36))

    company: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(255))
    platform: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="APPLIED")
    job_url: Mapped[str | None] = mapped_column(String(1000))

    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
