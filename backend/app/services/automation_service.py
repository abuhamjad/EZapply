"""Automation orchestration, persistence, and live event projection."""

import re
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.repositories import EZApplyRepository, decode_json
from app.services.event_broker import event_broker
from app.services.legacy_bot_service import LegacyBotService


SUPPORTED_PLATFORMS = ("linkedin", "naukri")
CONFIG_KEY = "automation_config"
EMPTY_STATS = {
    "jobs_found": 0,
    "applied": 0,
    "skipped": 0,
    "blacklisted": 0,
    "already_applied": 0,
    "failed": 0,
}


def default_config() -> dict[str, Any]:
    return {
        "platforms": {platform: False for platform in SUPPORTED_PLATFORMS},
        "job_type": "",
        "location": "",
        "min_salary": "",
        "apply_delay": 30,
        "keywords": [],
    }


def normalize_config(value: dict[str, Any] | None) -> dict[str, Any]:
    config = default_config()
    if not value:
        return config
    platforms = value.get("platforms", {})
    if isinstance(platforms, dict):
        for platform in SUPPORTED_PLATFORMS:
            if platform in platforms:
                config["platforms"][platform] = bool(platforms[platform])
    for field in ("job_type", "location", "min_salary"):
        provided = value.get(field)
        if isinstance(provided, str):
            config[field] = provided.strip()
    delay = value.get("apply_delay")
    if isinstance(delay, int) and 1 <= delay <= 600:
        config["apply_delay"] = delay
    keywords = value.get("keywords", [])
    if isinstance(keywords, list):
        seen: set[str] = set()
        config["keywords"] = [
            keyword.strip()
            for keyword in keywords
            if isinstance(keyword, str)
            and keyword.strip()
            and not (keyword.casefold() in seen or seen.add(keyword.casefold()))
        ]
    return config


def ui_status(runtime_status: str, pending_question: Any) -> str:
    if pending_question:
        return "paused"
    if runtime_status == "paused":
        return "paused"
    if runtime_status in {"running", "signing_in", "stopping"}:
        return "running"
    return "stopped"


class AutomationService:
    """Coordinates browser runs while keeping all visible data persistent."""

    def __init__(self) -> None:
        self.runner = LegacyBotService(self.record_runtime_event)

    @staticmethod
    def _repository(database: Session) -> EZApplyRepository:
        return EZApplyRepository(database)

    @staticmethod
    def _run_stats(run: Any | None) -> dict[str, int]:
        if run is None:
            return dict(EMPTY_STATS)
        stored = decode_json(run.stats_json, {})
        stats = dict(EMPTY_STATS)
        if isinstance(stored, dict):
            for key, value in stored.items():
                if isinstance(value, int):
                    stats[key] = value
        return stats

    def config(self, database: Session) -> dict[str, Any]:
        repository = self._repository(database)
        config = normalize_config(repository.get_json_setting(CONFIG_KEY, default_config()))
        return {**config, "available_platforms": list(SUPPORTED_PLATFORMS)}

    def update_config(self, database: Session, value: dict[str, Any]) -> dict[str, Any]:
        repository = self._repository(database)
        config = normalize_config(value)
        repository.save_json_setting(CONFIG_KEY, config)
        return {**config, "available_platforms": list(SUPPORTED_PLATFORMS)}

    def _event_payload(self, event: Any) -> dict[str, Any]:
        return {
            "id": event.id,
            "run_id": event.run_id,
            "type": event.event_type,
            "message": event.message,
            "data": decode_json(event.data_json, {}),
            "created_at": event.created_at,
        }

    def event_history(self, database: Session, run_id: int | None) -> list[dict[str, Any]]:
        return [
            self._event_payload(event)
            for event in self._repository(database).list_events(run_id)
        ]

    def _save_event(
        self,
        repository: EZApplyRepository,
        run_id: int | None,
        event_type: str,
        message: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        event = repository.add_event(run_id, event_type, message, data)
        payload = self._event_payload(event)
        event_broker.publish(payload)
        return payload

    def _system_event(
        self,
        repository: EZApplyRepository,
        run_id: int | None,
        event_type: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._save_event(repository, run_id, event_type, message, data or {})

    @staticmethod
    def _parse_application(message: str) -> tuple[str, str] | None:
        match = re.search(
            r"(?:Applied|DRY RUN(?:\s+\w+)?)\s*:\s*(?P<role>.+?)(?:\s+@\s+(?P<company>.+))?$",
            message,
            re.IGNORECASE,
        )
        if match is None:
            return None
        role = match.group("role").strip()
        company = (match.group("company") or "").strip()
        return (role, company) if role else None

    def record_runtime_event(self, run_id: int | None, event: dict[str, Any]) -> None:
        """Persist a browser event, then broadcast it to every UI client."""
        database = SessionLocal()
        try:
            repository = self._repository(database)
            event_type = str(event.get("type", "info"))
            message = str(event.get("message", ""))
            data = event.get("data") if isinstance(event.get("data"), dict) else {}
            self._save_event(repository, run_id, event_type, message, data)
            run = repository.get_run(run_id) if run_id is not None else None
            if run is not None:
                if event_type == "stats":
                    repository.update_run(run.id, stats=data)
                elif event_type == "complete":
                    repository.update_run(
                        run.id,
                        status="stopped",
                        stats=data if data else self._run_stats(run),
                        completed_at=datetime.utcnow(),
                    )
                elif event_type == "question":
                    repository.update_run(run.id, status="paused")
                elif event_type == "error":
                    repository.update_run(run.id, error_message=message)

                application = self._parse_application(message)
                if event_type == "success" and application is not None:
                    repository.add_application(
                        run_id=run.id,
                        platform=run.platform or "",
                        role=application[0],
                        company=application[1],
                        location="",
                        status="submitted",
                        applied_at=datetime.utcnow(),
                    )
        finally:
            database.close()

    def start(self, database: Session, request_config: dict[str, Any] | None = None) -> dict[str, Any]:
        if request_config is not None:
            self.update_config(database, request_config)
        repository = self._repository(database)
        config = normalize_config(repository.get_json_setting(CONFIG_KEY, default_config()))
        selected = [platform for platform, enabled in config["platforms"].items() if enabled]
        if not selected:
            raise ValueError("Select a supported platform first.")
        if len(selected) > 1:
            raise ValueError("Select one platform per browser run.")

        resume = repository.get_active_resume()
        parsed_resume = decode_json(resume.parsed_json, {}) if resume else {}
        if not config["keywords"]:
            saved_keywords = repository.get_json_setting(
                "saved_keywords", {"saved_keywords": []}
            )
            if isinstance(saved_keywords, dict):
                config["keywords"] = saved_keywords.get("saved_keywords", [])
        if not config["keywords"] and isinstance(parsed_resume, dict):
            config["keywords"] = parsed_resume.get("search_keywords", [])
        if not config["keywords"]:
            raise ValueError("Add at least one search keyword before starting.")

        run = repository.create_run("signing_in", selected[0], config)
        self._system_event(repository, run.id, "info", "Opening browser sign-in.")
        try:
            self.runner.start(
                run.id,
                config,
                parsed_resume if isinstance(parsed_resume, dict) else {},
                resume.storage_path if resume else None,
            )
        except (RuntimeError, ValueError) as exc:
            repository.update_run(
                run.id,
                status="failed",
                error_message=str(exc),
                completed_at=datetime.utcnow(),
            )
            self._system_event(repository, run.id, "error", str(exc))
            raise ValueError(str(exc)) from exc
        return self.status(database)

    def status(self, database: Session) -> dict[str, Any]:
        repository = self._repository(database)
        run = repository.get_latest_run()
        runtime = self.runner.status()
        runtime_status = str(runtime.get("status", "idle"))
        pending = runtime.get("pending_question")
        status = ui_status(runtime_status, pending)
        if run is not None and run.status not in {"failed", "stopped"}:
            completed_at = datetime.utcnow() if status == "stopped" else None
            repository.update_run(run.id, status=status, completed_at=completed_at)
            run = repository.get_run(run.id)
        pending_question = None
        if isinstance(pending, dict):
            pending_data = pending.get("data") if isinstance(pending.get("data"), dict) else {}
            pending_question = {
                "field": str(pending_data.get("field", "")),
                "job": str(pending_data.get("job", "")),
                "message": str(pending.get("message", "")),
            }
        return {
            "status": status,
            "run_id": run.id if run else None,
            "stats": runtime.get("stats") or self._run_stats(run),
            "pending_question": pending_question,
            "updated_at": datetime.utcnow(),
        }

    def pause(self, database: Session) -> dict[str, Any]:
        run = self._repository(database).get_latest_run()
        if run is None:
            raise ValueError("No active browser run.")
        self.runner.pause()
        repository = self._repository(database)
        repository.update_run(run.id, status="paused")
        self._system_event(repository, run.id, "info", "Automation paused.")
        return self.status(database)

    def resume(self, database: Session) -> dict[str, Any]:
        run = self._repository(database).get_latest_run()
        if run is None:
            raise ValueError("No active browser run.")
        self.runner.resume()
        repository = self._repository(database)
        repository.update_run(run.id, status="running")
        self._system_event(repository, run.id, "info", "Automation resumed.")
        return self.status(database)

    def stop(self, database: Session) -> dict[str, Any]:
        run = self._repository(database).get_latest_run()
        if run is None:
            return self.status(database)
        self.runner.stop()
        repository = self._repository(database)
        repository.update_run(run.id, status="stopping")
        self._system_event(repository, run.id, "info", "Stop requested.")
        return self.status(database)

    def submit_response(self, database: Session, answer: str) -> dict[str, Any]:
        self.runner.submit_response(answer)
        run = self._repository(database).get_latest_run()
        if run is not None:
            repository = self._repository(database)
            repository.update_run(run.id, status="running")
            self._system_event(repository, run.id, "info", "Response submitted.")
        return self.status(database)


automation_service = AutomationService()
