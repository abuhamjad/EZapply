# Bot Manager — Orchestrates bot sessions in threads
import threading, queue, time, json, os
from typing import Dict, Optional
from linkedin_bot import LinkedinBot
from naukri_bot import NaukriBot

class BotManager:
    def __init__(self):
        self.event_queue = queue.Queue()
        self.response_queue = queue.Queue()   # User answers to bot questions
        self.linkedin_bot = None
        self.naukri_bot = None
        self.threads = []
        self.status = "idle"  # idle, running, stopping
        self.config = {}
        self.resume_data = {}
        self.combined_stats = {"jobs_found":0,"applied":0,"skipped":0,"blacklisted":0,"already_applied":0,"failed":0}
        self.log_history = []
        self.pending_question = None  # Track current unanswered question

    def start(self, config: Dict, resume_data: Dict = None):
        if self.status == "running":
            return {"error": "Bot already running"}
        self.config = config
        self.resume_data = resume_data or {}
        self.status = "running"
        self.combined_stats = {"jobs_found":0,"applied":0,"skipped":0,"blacklisted":0,"already_applied":0,"failed":0}
        self.log_history = []
        self.pending_question = None
        # Clear queues
        for q in (self.event_queue, self.response_queue):
            while not q.empty():
                try: q.get_nowait()
                except: break
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
            return {"error": "No platforms configured with credentials"}
        return {"status": "started", "platforms": platforms}

    def _run_linkedin(self):
        self.linkedin_bot = LinkedinBot(self.config, self.event_queue, self.resume_data, self.response_queue)
        try:
            self.emit_event("info", "🚀 Starting LinkedIn bot...")
            self.linkedin_bot.setup_driver()
            if self.linkedin_bot.login():
                self.linkedin_bot.apply_to_jobs()
            else:
                self.emit_event("error", "❌ LinkedIn login failed")
        except Exception as e:
            self.emit_event("error", f"❌ LinkedIn crash: {str(e)[:80]}")
        finally:
            self.linkedin_bot.cleanup()
            self._check_all_done()

    def _run_naukri(self):
        self.naukri_bot = NaukriBot(self.config, self.event_queue, self.resume_data)
        try:
            self.emit_event("info", "🚀 Starting Naukri bot...")
            self.naukri_bot.setup_driver()
            if self.naukri_bot.login():
                self.naukri_bot.apply_to_jobs()
            else:
                self.emit_event("error", "❌ Naukri login failed")
        except Exception as e:
            self.emit_event("error", f"❌ Naukri crash: {str(e)[:80]}")
        finally:
            self.naukri_bot.cleanup()
            self._check_all_done()

    def _check_all_done(self):
        alive = any(t.is_alive() for t in self.threads)
        if not alive:
            self.status = "idle"
            self.emit_event("complete", "🏁 All bots finished!", self.combined_stats)

    def emit_event(self, etype, msg, data=None):
        evt = {"type":etype,"message":msg,"data":data or {},"timestamp":time.strftime("%H:%M:%S")}
        if etype == "question":
            self.pending_question = evt
        self.event_queue.put(evt)

    def submit_response(self, answer: str):
        """User submits answer to bot's question."""
        self.pending_question = None
        self.response_queue.put(answer)
        return {"status": "ok"}

    def stop(self):
        self.status = "stopping"
        if self.linkedin_bot: self.linkedin_bot.stop()
        if self.naukri_bot: self.naukri_bot.stop()
        # Unblock any waiting question
        self.response_queue.put("__SKIP__")
        self.emit_event("info", "⏹️ Stop signal sent to all bots")
        return {"status": "stopping"}

    def get_status(self):
        return {"status": self.status, "stats": self.combined_stats, "pending_question": self.pending_question}

    def get_events(self):
        """Generator yielding SSE events."""
        while True:
            try:
                event = self.event_queue.get(timeout=30)
                if event.get("type") == "stats":
                    self.combined_stats.update(event.get("data", {}))
                self.log_history.append(event)
                # Keep last 500 logs
                if len(self.log_history) > 500:
                    self.log_history = self.log_history[-500:]
                yield event
            except queue.Empty:
                yield {"type": "heartbeat", "message": "", "data": {}, "timestamp": time.strftime("%H:%M:%S")}

