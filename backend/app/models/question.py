import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class ScreeningQuestion(Base):
    """An unresolved question encountered mid-run, awaiting user input."""

    __tablename__ = "screening_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bot_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("bot_runs.id"))

    question_text: Mapped[str] = mapped_column(Text)
    field_type: Mapped[str] = mapped_column(String(50))  # text | radio | select | checkbox
    job_title: Mapped[str | None] = mapped_column(String(255))
    company: Mapped[str | None] = mapped_column(String(255))

    answer: Mapped[str | None] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class QuestionKnowledge(Base):
    """Learned answer bank: question_text -> answer, reused across future runs."""

    __tablename__ = "question_knowledge"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_text: Mapped[str] = mapped_column(Text, unique=True)
    answer: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
