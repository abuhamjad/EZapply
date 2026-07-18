"""Persistent entities owned by the FastAPI backend.

The desktop app has one local user, so profile and preference records are
stored as singletons rather than pretending that sample users exist.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text

from app.database.base import Base


def utcnow() -> datetime:
    """Return a timezone-neutral UTC timestamp for SQLite."""
    return datetime.utcnow()


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    key = Column(Text, nullable=False, unique=True, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    fields_json = Column(Text, nullable=False, default="[]")
    skills_json = Column(Text, nullable=False, default="[]")
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True)
    filename = Column(Text, nullable=False)
    storage_path = Column(Text, nullable=False, unique=True)
    content_type = Column(Text, nullable=True)
    size_bytes = Column(Integer, nullable=False)
    parsed_json = Column(Text, nullable=False, default="{}")
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)


class CoverLetterTemplate(Base):
    __tablename__ = "cover_letter_templates"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    content = Column(Text, nullable=False, default="")
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)


class AutomationRun(Base):
    __tablename__ = "automation_runs"

    id = Column(Integer, primary_key=True)
    status = Column(Text, nullable=False, index=True)
    platform = Column(Text, nullable=True)
    config_json = Column(Text, nullable=False, default="{}")
    stats_json = Column(Text, nullable=False, default="{}")
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False, default=utcnow)
    completed_at = Column(DateTime, nullable=True)


class AutomationEvent(Base):
    __tablename__ = "automation_events"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("automation_runs.id"), nullable=True, index=True)
    event_type = Column(Text, nullable=False, index=True)
    message = Column(Text, nullable=False)
    data_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, nullable=False, default=utcnow, index=True)


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("automation_runs.id"), nullable=True, index=True)
    platform = Column(Text, nullable=False, index=True)
    role = Column(Text, nullable=False)
    company = Column(Text, nullable=False, default="")
    location = Column(Text, nullable=False, default="")
    status = Column(Text, nullable=False, index=True)
    applied_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)
