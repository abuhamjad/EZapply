"""SQLite persistence for EZApply's live data.

Route handlers never access SQLAlchemy directly.  Services use this repository
to make the source of every dashboard value explicit.
"""

import json
from datetime import datetime
from typing import Any, Iterable

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import (
    AutomationEvent,
    AutomationRun,
    CoverLetterTemplate,
    JobApplication,
    Resume,
    Setting,
    UserProfile,
)


def decode_json(value: str | None, fallback: Any) -> Any:
    try:
        return json.loads(value) if value else fallback
    except (TypeError, json.JSONDecodeError):
        return fallback


def encode_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


class EZApplyRepository:
    """Repository for the local desktop user's records."""

    def __init__(self, database: Session):
        self.database = database

    def get_json_setting(self, key: str, default: Any) -> Any:
        record = self.database.query(Setting).filter(Setting.key == key).one_or_none()
        return decode_json(record.value, default) if record else default

    def save_json_setting(self, key: str, value: Any) -> Any:
        record = self.database.query(Setting).filter(Setting.key == key).one_or_none()
        if record is None:
            record = Setting(key=key, value=encode_json(value))
            self.database.add(record)
        else:
            record.value = encode_json(value)
        self.database.commit()
        return value

    def get_profile(self) -> UserProfile | None:
        return self.database.query(UserProfile).order_by(UserProfile.id).first()

    def save_profile(self, fields: list[dict[str, str]], skills: list[str]) -> UserProfile:
        profile = self.get_profile()
        if profile is None:
            profile = UserProfile()
            self.database.add(profile)
        profile.fields_json = encode_json(fields)
        profile.skills_json = encode_json(skills)
        self.database.commit()
        self.database.refresh(profile)
        return profile

    def list_resumes(self) -> list[Resume]:
        return self.database.query(Resume).order_by(desc(Resume.created_at)).all()

    def get_resume(self, resume_id: int) -> Resume | None:
        return self.database.query(Resume).filter(Resume.id == resume_id).one_or_none()

    def get_active_resume(self) -> Resume | None:
        return self.database.query(Resume).filter(Resume.is_active.is_(True)).first()

    def add_resume(
        self,
        filename: str,
        storage_path: str,
        content_type: str | None,
        size_bytes: int,
        parsed_data: dict[str, Any],
    ) -> Resume:
        self.database.query(Resume).update({Resume.is_active: False})
        resume = Resume(
            filename=filename,
            storage_path=storage_path,
            content_type=content_type,
            size_bytes=size_bytes,
            parsed_json=encode_json(parsed_data),
            is_active=True,
        )
        self.database.add(resume)
        self.database.commit()
        self.database.refresh(resume)
        return resume

    def delete_resume(self, resume: Resume) -> None:
        self.database.delete(resume)
        self.database.commit()

    def list_templates(self) -> list[CoverLetterTemplate]:
        return (
            self.database.query(CoverLetterTemplate)
            .order_by(desc(CoverLetterTemplate.updated_at))
            .all()
        )

    def add_template(self, name: str, content: str) -> CoverLetterTemplate:
        template = CoverLetterTemplate(name=name, content=content)
        self.database.add(template)
        self.database.commit()
        self.database.refresh(template)
        return template

    def delete_template(self, template_id: int) -> bool:
        template = (
            self.database.query(CoverLetterTemplate)
            .filter(CoverLetterTemplate.id == template_id)
            .one_or_none()
        )
        if template is None:
            return False
        self.database.delete(template)
        self.database.commit()
        return True

    def create_run(
        self,
        status: str,
        platform: str | None,
        config: dict[str, Any],
    ) -> AutomationRun:
        run = AutomationRun(
            status=status,
            platform=platform,
            config_json=encode_json(config),
            stats_json=encode_json({}),
        )
        self.database.add(run)
        self.database.commit()
        self.database.refresh(run)
        return run

    def get_run(self, run_id: int) -> AutomationRun | None:
        return self.database.query(AutomationRun).filter(AutomationRun.id == run_id).one_or_none()

    def get_latest_run(self) -> AutomationRun | None:
        return self.database.query(AutomationRun).order_by(desc(AutomationRun.id)).first()

    def update_run(
        self,
        run_id: int,
        *,
        status: str | None = None,
        stats: dict[str, Any] | None = None,
        error_message: str | None = None,
        completed_at: datetime | None = None,
    ) -> AutomationRun | None:
        run = self.get_run(run_id)
        if run is None:
            return None
        if status is not None:
            run.status = status
        if stats is not None:
            run.stats_json = encode_json(stats)
        if error_message is not None:
            run.error_message = error_message
        if completed_at is not None:
            run.completed_at = completed_at
        self.database.commit()
        self.database.refresh(run)
        return run

    def add_event(
        self,
        run_id: int | None,
        event_type: str,
        message: str,
        data: dict[str, Any],
    ) -> AutomationEvent:
        event = AutomationEvent(
            run_id=run_id,
            event_type=event_type,
            message=message,
            data_json=encode_json(data),
        )
        self.database.add(event)
        self.database.commit()
        self.database.refresh(event)
        return event

    def list_events(self, run_id: int | None, limit: int = 100) -> list[AutomationEvent]:
        query = self.database.query(AutomationEvent)
        if run_id is not None:
            query = query.filter(AutomationEvent.run_id == run_id)
        return query.order_by(desc(AutomationEvent.id)).limit(limit).all()[::-1]

    def add_application(
        self,
        run_id: int | None,
        platform: str,
        role: str,
        company: str,
        location: str,
        status: str,
        applied_at: datetime | None,
    ) -> JobApplication:
        application = JobApplication(
            run_id=run_id,
            platform=platform,
            role=role,
            company=company,
            location=location,
            status=status,
            applied_at=applied_at,
        )
        self.database.add(application)
        self.database.commit()
        self.database.refresh(application)
        return application

    def list_applications(self) -> list[JobApplication]:
        return (
            self.database.query(JobApplication)
            .order_by(desc(JobApplication.applied_at), desc(JobApplication.created_at))
            .all()
        )

    def list_applications_since(self, start: datetime) -> Iterable[JobApplication]:
        return (
            self.database.query(JobApplication)
            .filter(JobApplication.created_at >= start)
            .order_by(JobApplication.created_at)
            .all()
        )
