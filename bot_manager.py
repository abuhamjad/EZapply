# Bot Manager — Orchestrates bot sessions in threads
import threading, queue, time, json, os
from typing import Dict, Optional
from linkedin_bot import LinkedinBot
from naukri_bot import NaukriBot
from browser_driver import create_driver
import constants

class BotManager:
    def __init__(self):
        self.event_queue = queue.Queue()
        self.response_queue = queue.Queue()   # User answers to bot questions
        self.linkedin_bot = None
        self.naukri_bot = None
        self.threads = []
        self.status = "idle"  # idle, running, stopping, signing_in
        self.config = {}
        self.resume_data = {}
        self.combined_stats = {"jobs_found":0,"applied":0,"skipped":0,"blacklisted":0,"already_applied":0,"failed":0}
        self.log_history = []
        self.pending_question = None  # Track current unanswered question
        self.signin_driver = None  # Browser for manual sign-in
        self.signin_platform = None
        self.paused = False

    def start(self, config: Dict, resume_data: Dict = None):
        if self.status == "running":
            return {"error": "Bot already running"}
        self.config = config
        self.resume_data = resume_data or {}
        self.status = "running"
        self.combined_stats = {"jobs_found":0,"applied":0,"skipped":0,"blacklisted":0,"already_applied":0,"failed":0}
        self.log_history = []
        self.pending_question = None
        self.paused = False
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

    def signin_redirect(self, platform, config, resume_data=None):
        """Open browser to platform login page. Poll for sign-in. Auto-start bot."""
        if self.status in ("running", "signing_in"):
            return {"error": "Bot already active"}
        self.config = config
        self.resume_data = resume_data or {}
        self.signin_platform = platform
        self.status = "signing_in"
        self.combined_stats = {"jobs_found":0,"applied":0,"skipped":0,"blacklisted":0,"already_applied":0,"failed":0}
        self.log_history = []
        self.pending_question = None
        self.paused = False
        # Clear queues
        for q in (self.event_queue, self.response_queue):
            while not q.empty():
                try: q.get_nowait()
                except: break
        t = threading.Thread(target=self._signin_and_run, args=(platform,), daemon=True)
        t.start()
        self.threads = [t]
        return {"status": "signing_in", "platform": platform}

    def _signin_and_run(self, platform):
        """Open browser → wait for manual sign-in → run bot."""
        try:
            self.emit_event("info", f"🌐 Opening {platform.title()} sign-in page...")
            driver, browser_name = create_driver(headless=False)
            self.signin_driver = driver
            self.emit_event("info", f"🖥️ Using {browser_name.title()} browser")

            if platform == "linkedin":
                login_url = constants.LINKEDIN_LOGIN
                feed_url = constants.LINKEDIN_FEED
            else:
                login_url = constants.NAUKRI_LOGIN
                feed_url = constants.NAUKRI_BASE

            driver.get(login_url)
            self.emit_event("info", f"🔑 Sign in to {platform.title()} in the browser window...")

            # Poll for successful sign-in (up to 5 min)
            signed_in = False
            for attempt in range(100):  # 100 * 3s = 5 min
                if self.status == "stopping":
                    self.emit_event("info", "⏹️ Sign-in cancelled")
                    driver.quit()
                    self.status = "idle"
                    return
                time.sleep(3)
                try:
                    if platform == "linkedin":
                        signed_in = self._check_linkedin_signin(driver)
                    else:
                        signed_in = self._check_naukri_signin(driver)
                except:
                    continue
                if signed_in:
                    break

            if not signed_in:
                self.emit_event("error", "❌ Sign-in timed out (5 min)")
                driver.quit()
                self.status = "idle"
                return

            self.emit_event("success", f"✅ {platform.title()} sign-in successful!")
            self.emit_event("info", "🚀 Auto-starting bot...")
            self.status = "running"

            # Run bot with the already-signed-in driver
            if platform == "linkedin":
                self._run_linkedin_with_driver(driver)
            else:
                self._run_naukri_with_driver(driver)
        except Exception as e:
            self.emit_event("error", f"❌ Sign-in error: {str(e)[:80]}")
            self.status = "idle"
            try:
                if self.signin_driver:
                    self.signin_driver.quit()
            except: pass

    def _check_linkedin_signin(self, driver):
        """Check if user signed into LinkedIn."""
        from selenium.webdriver.common.by import By
        url = driver.current_url.lower()
        if "/feed" in url or "/mynetwork" in url or "/jobs" in url:
            if "/login" not in url and "/authwall" not in url:
                return True
        selectors = [
            "div.feed-identity-module", "div.global-nav__me",
            "img.global-nav__me-photo", "nav.global-nav",
            "div.scaffold-layout",
        ]
        for sel in selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el: return True
            except: continue
        return False

    def _check_naukri_signin(self, driver):
        """Check if user signed into Naukri."""
        from selenium.webdriver.common.by import By
        url = driver.current_url.lower()
        if "nlogin" in url or "/login" in url:
            return False
        indicators = [
            "div.nI-gNb-drawer__hamburger", "a.nI-gNb-header__userdp",
            "span.nI-gNb-header__userName", "a[href*='myprofile']",
        ]
        for sel in indicators:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el: return True
            except: continue
        # If on naukri.com and no login form visible
        login_fields = ["#usernameField", "#passwordField", "input[type='email']"]
        for sel in login_fields:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el and el.is_displayed(): return False
            except: continue
        if "naukri.com" in url:
            return True
        return False

    def _run_linkedin_with_driver(self, driver):
        """Run LinkedIn bot using pre-authenticated driver."""
        self.linkedin_bot = LinkedinBot(self.config, self.event_queue, self.resume_data, self.response_queue)
        self.linkedin_bot.driver = driver
        self.linkedin_bot.running = True
        try:
            self.linkedin_bot.save_cookies()
            self.linkedin_bot.apply_to_jobs()
        except Exception as e:
            self.emit_event("error", f"❌ LinkedIn crash: {str(e)[:80]}")
        finally:
            self.linkedin_bot.cleanup()
            self.status = "idle"
            self.emit_event("complete", "🏁 Bot finished!", self.combined_stats)

    def _run_naukri_with_driver(self, driver):
        """Run Naukri bot using pre-authenticated driver."""
        self.naukri_bot = NaukriBot(self.config, self.event_queue, self.resume_data)
        self.naukri_bot.driver = driver
        self.naukri_bot.running = True
        try:
            self.naukri_bot.save_cookies()
            self.naukri_bot.apply_to_jobs()
        except Exception as e:
            self.emit_event("error", f"❌ Naukri crash: {str(e)[:80]}")
        finally:
            self.naukri_bot.cleanup()
            self.status = "idle"
            self.emit_event("complete", "🏁 Bot finished!", self.combined_stats)

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
        current_thread = threading.current_thread()
        alive = any(
            thread is not current_thread and thread.is_alive()
            for thread in self.threads
        )
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
        self.paused = False
        if self.linkedin_bot: self.linkedin_bot.stop()
        if self.naukri_bot: self.naukri_bot.stop()
        # Unblock any waiting question
        self.response_queue.put("__SKIP__")
        # Kill sign-in browser if still open
        if self.signin_driver:
            try: self.signin_driver.quit()
            except: pass
            self.signin_driver = None
        self.emit_event("info", "⏹️ Stop signal sent to all bots")
        return {"status": "stopping"}

    def pause(self):
        if self.status != "running":
            return {"error": "Bot is not running"}
        self.paused = True
        if self.linkedin_bot:
            self.linkedin_bot.pause()
        if self.naukri_bot:
            self.naukri_bot.pause()
        self.status = "paused"
        self.emit_event("info", "Bot paused")
        return {"status": "paused"}

    def resume(self):
        if self.status != "paused":
            return {"error": "Bot is not paused"}
        self.paused = False
        if self.linkedin_bot:
            self.linkedin_bot.resume()
        if self.naukri_bot:
            self.naukri_bot.resume()
        self.status = "running"
        self.emit_event("info", "Bot resumed")
        return {"status": "running"}

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

