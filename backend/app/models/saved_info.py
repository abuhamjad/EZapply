from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class SavedInfo(Base):
    """
    Single-row-per-user table (desktop app = single local user).
    Holds personal details + job search preferences.
    """

    __tablename__ = "saved_info"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)

    # Personal details
    full_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    location: Mapped[str | None] = mapped_column(String(255))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    portfolio_url: Mapped[str | None] = mapped_column(String(500))

    # Job search preferences
    target_titles: Mapped[str | None] = mapped_column(Text)  # comma-separated
    target_locations: Mapped[str | None] = mapped_column(Text)
    salary_expectation: Mapped[str | None] = mapped_column(String(100))
    work_authorization: Mapped[str | None] = mapped_column(String(255))
    remote_preference: Mapped[str | None] = mapped_column(String(50))

    # Free-form custom Q&A the user has pre-answered, stored as JSON text
    custom_answers_json: Mapped[str | None] = mapped_column(Text)
    
    # Store keywords and templates as JSON lists of dicts
    saved_keywords_json: Mapped[str | None] = mapped_column(Text)
    cover_letter_templates_json: Mapped[str | None] = mapped_column(Text)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
