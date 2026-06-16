# ============================================================
# Bot Orchestrator — Lifecycle management for bot sessions
# ============================================================
import threading
import queue
import time
import json
import os
from typing import Dict, Optional
from datetime import datetime
from backend.core.logger import get_logger
from backend.core.events import event_bus
from backend.config import COOKIES_DIR

log = get_logger("orchestrator")


class BotOrchestrator:
    """Manages bot lifecycle across platforms."""

    def __init__(self):
        self.event_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.threads = []
        self.status = "idle"  # idle, running, stopping
        self.config = {}
        self.resume_data = {}
        self.combined_stats = {
            "jobs_found": 0, "applied": 0, "skipped": 0,
            "blacklisted": 0, "already_applied": 0, "failed": 0,
        }
        self.pending_question = None
        self._linkedin_bot = None
        self._naukri_bot = None

    def start(self, config: Dict, resume_data: Dict = None) -> Dict:
        """Start bot session on configured platforms."""
        if self.status == "running":
            return {"error": "Bot already running"}

        self.config = config
        self.resume_data = resume_data or {}
        self.status = "running"
        self.combined_stats = {
            "jobs_found": 0, "applied": 0, "skipped": 0,
            "blacklisted": 0, "already_applied": 0, "failed": 0,
        }
        self.pending_question = None

        # Clear queues
        for q in (self.event_queue, self.response_queue):
            while not q.empty():
                try:
                    q.get_nowait()
                except Exception:
                    break

        platforms = config.get("platforms", ["linkedin"])
        self.threads = []

        if "linkedin" in platforms and config.get("linkedin_email"):
            t = threading.Thread(target=self._run_linkedin, daemon=True)
            t.start()
            self.threads.append(t)

        if "naukri" in platforms and config.get("naukri_email"):
            t = threading.Thread(target=self._run_naukri, daemon=True)
            t.start()
            self.threads.append(t)

        if not self.threads:
            self.status = "idle"
            return {"error": "No platforms configured"}

        # Start event forwarding thread
        threading.Thread(target=self._forward_events, daemon=True).start()

        log.info(f"Bot started on platforms: {platforms}")
        return {"status": "started", "platforms": platforms}

    def _run_linkedin(self):
        """Run LinkedIn bot in thread."""
        # Import here to avoid circular deps
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from linkedin_bot import LinkedinBot

        self._linkedin_bot = LinkedinBot(
            self.config, self.event_queue, self.resume_data, self.response_queue
        )
        try:
            self._emit("info", "Starting LinkedIn bot...")
            self._linkedin_bot.setup_driver()
            if self._linkedin_bot.login():
                self._linkedin_bot.apply_to_jobs()
            else:
                self._emit("error", "LinkedIn login failed")
        except Exception as e:
            self._emit("error", f"LinkedIn crash: {str(e)[:80]}")
            log.exception("LinkedIn bot crashed")
        finally:
            self._linkedin_bot.cleanup()
            self._check_all_done()

    def _run_naukri(self):
        """Run Naukri bot in thread."""
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from naukri_bot import NaukriBot

        self._naukri_bot = NaukriBot(
            self.config, self.event_queue, self.resume_data
        )
        try:
            self._emit("info", "Starting Naukri bot...")
            self._naukri_bot.setup_driver()
            if self._naukri_bot.login():
                self._naukri_bot.apply_to_jobs()
            else:
                self._emit("error", "Naukri login failed")
        except Exception as e:
            self._emit("error", f"Naukri crash: {str(e)[:80]}")
            log.exception("Naukri bot crashed")
        finally:
            self._naukri_bot.cleanup()
            self._check_all_done()

    def _check_all_done(self):
        alive = any(t.is_alive() for t in self.threads)
        if not alive:
            self.status = "idle"
            self._emit("complete", "All bots finished!", self.combined_stats)
            log.info(f"Session complete. Stats: {self.combined_stats}")

    def _emit(self, etype: str, message: str, data: Dict = None):
        event = {
            "type": etype, "message": message,
            "data": data or {}, "timestamp": time.strftime("%H:%M:%S"),
        }
        if etype == "question":
            self.pending_question = event
        self.event_queue.put(event)

    def _forward_events(self):
        """Forward queue events to WebSocket event bus."""
        while self.status == "running":
            try:
                event = self.event_queue.get(timeout=5)
                if event.get("type") == "stats":
                    self.combined_stats.update(event.get("data", {}))
                # Forward to WebSocket
                event_bus.emit_sync(event["type"], event["message"], event.get("data"))
            except queue.Empty:
                continue
            except Exception as e:
                log.warning(f"Event forward error: {e}")

    def stop(self) -> Dict:
        self.status = "stopping"
        if self._linkedin_bot:
            self._linkedin_bot.stop()
        if self._naukri_bot:
            self._naukri_bot.stop()
        self.response_queue.put("__SKIP__")
        self._emit("info", "Stop signal sent to all bots")
        return {"status": "stopping"}

    def submit_response(self, answer: str) -> Dict:
        self.pending_question = None
        self.response_queue.put(answer)
        return {"status": "ok"}

    def get_status(self) -> Dict:
        return {
            "status": self.status,
            "stats": self.combined_stats,
            "pending_question": self.pending_question,
        }


# Singleton
bot_orchestrator = BotOrchestrator()
