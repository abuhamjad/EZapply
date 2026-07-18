"""Safe FastAPI gateway for the existing browser automation runner."""

import queue
import sys
from pathlib import Path
from threading import Lock, Thread
from typing import Any, Callable


class LegacyBotService:
    """Own one legacy manager and forward its queue exactly once."""

    def __init__(self, on_event: Callable[[int | None, dict[str, Any]], None]) -> None:
        self._on_event = on_event
        self._manager: Any | None = None
        self._run_id: int | None = None
        self._lock = Lock()
        self._pump_started = False
        self._load_error: str | None = None

    @staticmethod
    def _repository_root() -> Path:
        return Path(__file__).resolve().parents[3]

    def _get_manager(self) -> Any:
        if self._manager is not None:
            return self._manager
        if self._load_error is not None:
            raise RuntimeError(self._load_error)

        root = str(self._repository_root())
        if root not in sys.path:
            sys.path.insert(0, root)
        try:
            from bot_manager import BotManager

            self._manager = BotManager()
            return self._manager
        except Exception as exc:  # pragma: no cover - depends on local browsers/packages
            self._load_error = f"Browser runner unavailable: {exc}"
            raise RuntimeError(self._load_error) from exc

    def _ensure_pump(self) -> None:
        if self._pump_started:
            return
        self._pump_started = True
        Thread(target=self._pump_events, name="ezapply-bot-events", daemon=True).start()

    def _pump_events(self) -> None:
        while True:
            try:
                manager = self._get_manager()
                event = manager.event_queue.get(timeout=1)
                if event.get("type") == "stats":
                    manager.combined_stats.update(event.get("data", {}))
                if event.get("type") == "question":
                    manager.pending_question = event
                manager.log_history.append(event)
                if len(manager.log_history) > 500:
                    manager.log_history = manager.log_history[-500:]
                with self._lock:
                    run_id = self._run_id
                self._on_event(run_id, event)
            except queue.Empty:
                continue
            except Exception:
                # A later start can retry loading the local browser runner.
                continue

    @staticmethod
    def _legacy_config(config: dict[str, Any], resume_path: str | None) -> dict[str, Any]:
        selected_platforms = [
            platform
            for platform, enabled in config.get("platforms", {}).items()
            if enabled
        ]
        location = config.get("location", "").strip()
        job_type = config.get("job_type", "").strip()
        return {
            "platforms": selected_platforms,
            "keywords": config.get("keywords", []),
            "location": [location] if location else [],
            "job_types": [job_type.title()] if job_type else [],
            "remote": ["Remote"] if location.lower() == "remote" else [],
            "max_applications": 50,
            "resume_path": resume_path or "",
            "headless": False,
            "dry_run": False,
        }

    def start(
        self,
        run_id: int,
        config: dict[str, Any],
        resume_data: dict[str, Any],
        resume_path: str | None,
    ) -> dict[str, Any]:
        manager = self._get_manager()
        self._ensure_pump()
        legacy_config = self._legacy_config(config, resume_path)
        platforms = legacy_config["platforms"]
        if not platforms:
            raise ValueError("Select at least one supported platform.")
        if len(platforms) > 1:
            raise ValueError("Select one platform per browser run.")

        with self._lock:
            if manager.status in {"running", "signing_in", "paused", "stopping"}:
                raise ValueError("A browser run is already active.")
            self._run_id = run_id
            result = manager.signin_redirect(platforms[0], legacy_config, resume_data)
        if result.get("error"):
            raise ValueError(result["error"])
        return result

    def status(self) -> dict[str, Any]:
        try:
            manager = self._get_manager()
            return manager.get_status()
        except RuntimeError:
            return {"status": "idle", "stats": {}, "pending_question": None}

    def pause(self) -> None:
        manager = self._get_manager()
        if not hasattr(manager, "pause"):
            raise ValueError("Pause is unavailable for this runner.")
        result = manager.pause()
        if result.get("error"):
            raise ValueError(result["error"])

    def resume(self) -> None:
        manager = self._get_manager()
        if not hasattr(manager, "resume"):
            raise ValueError("Resume is unavailable for this runner.")
        result = manager.resume()
        if result.get("error"):
            raise ValueError(result["error"])

    def stop(self) -> None:
        manager = self._get_manager()
        result = manager.stop()
        if result.get("error"):
            raise ValueError(result["error"])

    def submit_response(self, answer: str) -> None:
        manager = self._get_manager()
        result = manager.submit_response(answer)
        if result.get("error"):
            raise ValueError(result["error"])
