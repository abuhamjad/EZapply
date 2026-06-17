# ============================================================
# Database Models — SQLAlchemy ORM
# ============================================================
import json
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, Text, Boolean, Float, DateTime, ForeignKey, Index, String
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text, unique=True, nullable=False)
    display_name = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(Text, nullable=False)  # "Software Engineer", "Data Scientist"
    email = Column(Text)
    phone = Column(Text)
    linkedin_url = Column(Text)
    github_url = Column(Text)
    portfolio_url = Column(Text)
    experience_years = Column(Float, default=0)
    experience_level = Column(Text, default="Entry")
    skills = Column(Text, default="[]")  # JSON array
    preferred_locations = Column(Text, default='["India"]')  # JSON array
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(Text, default="INR")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profiles")
    resumes = relationship("Resume", back_populates="profile", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="profile")
    saved_answers = relationship("SavedAnswer", back_populates="profile", cascade="all, delete-orphan")

    @property
    def skills_list(self) -> list:
        try:
            return json.loads(self.skills) if self.skills else []
        except (json.JSONDecodeError, TypeError):
            return []

    @skills_list.setter
    def skills_list(self, val: list):
        self.skills = json.dumps(val)

    @property
    def locations_list(self) -> list:
        try:
            return json.loads(self.preferred_locations) if self.preferred_locations else []
        except (json.JSONDecodeError, TypeError):
            return []


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    filename = Column(Text, nullable=False)
    filepath = Column(Text, nullable=False)
    file_type = Column(Text, nullable=False)  # PDF, DOCX
    file_size = Column(Integer)
    parsed_data = Column(Text)  # JSON
    ats_score = Column(Float)
    is_primary = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="resumes")

    @property
    def parsed(self) -> dict:
        try:
            return json.loads(self.parsed_data) if self.parsed_data else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    @parsed.setter
    def parsed(self, val: dict):
        self.parsed_data = json.dumps(val)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(Text, nullable=False)  # linkedin, naukri
    external_id = Column(Text)
    title = Column(Text, nullable=False)
    company = Column(Text)
    location = Column(Text)
    description = Column(Text)
    job_url = Column(Text)
    job_type = Column(Text)
    remote_type = Column(Text)
    salary_range = Column(Text)
    experience_required = Column(Text)
    posted_date = Column(Text)
    easy_apply = Column(Boolean, default=False)
    match_score = Column(Float)
    confidence_score = Column(Float)
    risk_score = Column(Float)
    missing_skills = Column(Text)  # JSON array
    ai_reasoning = Column(Text)  # JSON
    apply_recommendation = Column(Text)  # STRONG_APPLY, GOOD_APPLY, OPTIONAL, SKIP
    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    applications = relationship("Application", back_populates="job")

    __table_args__ = (
        Index("idx_jobs_platform", "platform"),
        Index("idx_jobs_match_score", "match_score"),
    )


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    status = Column(Text, nullable=False, default="queued")
    # queued, analyzing, ready, applying, submitted, failed, interview, rejected, offer
    answers = Column(Text)  # JSON
    cover_note = Column(Text)
    applied_at = Column(DateTime)
    response_received_at = Column(DateTime)
    notes = Column(Text)
    error_message = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    job = relationship("Job", back_populates="applications")
    profile = relationship("Profile", back_populates="applications")

    __table_args__ = (
        Index("idx_applications_status", "status"),
        Index("idx_applications_job", "job_id"),
    )


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Text, nullable=False)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    jobs_discovered = Column(Integer, default=0)
    jobs_analyzed = Column(Integer, default=0)
    applications_submitted = Column(Integer, default=0)
    applications_failed = Column(Integer, default=0)
    avg_match_score = Column(Float)
    top_skills_matched = Column(Text)  # JSON
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (Index("idx_analytics_date", "date"),)


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(Text, unique=True, nullable=False)
    value = Column(Text, nullable=False)
    is_encrypted = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SavedAnswer(Base):
    __tablename__ = "saved_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    question_key = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source = Column(Text, default="user")  # user, ai
    times_used = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="saved_answers")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Text, nullable=False)  # match, applied, failed, interview
    title = Column(Text, nullable=False)
    message = Column(Text)
    data = Column(Text)  # JSON
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (Index("idx_notifications_read", "is_read"),)


class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Text, nullable=False)
    source = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text)  # JSON
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_logs_level", "level"),
        Index("idx_logs_created", "created_at"),
    )
