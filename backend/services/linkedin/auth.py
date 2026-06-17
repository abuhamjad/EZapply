# ============================================================
# LinkedIn Auth — Login + cookie management
# ============================================================
import hashlib
import json
import os
import time
from typing import Optional
from backend.config import COOKIES_DIR, LINKEDIN_BASE, LINKEDIN_FEED, LINKEDIN_LOGIN
from backend.services.encryption import encryption_service
from backend.core.logger import get_logger

log = get_logger("linkedin.auth")


class LinkedInAuth:
    """Handle LinkedIn authentication with cookie persistence."""

    def __init__(self, driver):
        self.driver = driver

    def _cookie_path(self, email: str) -> str:
        h = hashlib.md5(email.encode("utf-8")).hexdigest()
        return str(COOKIES_DIR / f"linkedin_{h}.json")

    def load_cookies(self, email: str) -> bool:
        """Load saved cookies for email. Returns True if loaded."""
        path = self._cookie_path(email)
        if not os.path.exists(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                encrypted = f.read()
            data = encryption_service.decrypt(encrypted)
            cookies = json.loads(data)
            self.driver.delete_all_cookies()
            for c in cookies:
                try:
                    self.driver.add_cookie(c)
                except Exception:
                    pass
            log.info("Cookies loaded")
            return True
        except Exception as e:
            log.warning(f"Cookie load failed: {e}")
            return False

    def save_cookies(self, email: str):
        """Save current browser cookies encrypted."""
        path = self._cookie_path(email)
        try:
            cookies = self.driver.get_cookies()
            data = json.dumps(cookies)
            encrypted = encryption_service.encrypt(data)
            with open(path, "w", encoding="utf-8") as f:
                f.write(encrypted)
            log.info("Cookies saved")
        except Exception as e:
            log.warning(f"Cookie save failed: {e}")

    def is_logged_in(self) -> bool:
        """Check if currently logged into LinkedIn."""
        from selenium.webdriver.common.by import By
        url = self.driver.current_url
        if "/feed" in url or "/mynetwork" in url or "/jobs" in url:
            if "/login" not in url and "/authwall" not in url:
                return True
        selectors = [
            "div.feed-identity-module", "div.global-nav__me",
            "img.global-nav__me-photo", "a[href*='/me/']",
            "div.scaffold-layout", "nav.global-nav",
        ]
        for sel in selectors:
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, sel)
                if el:
                    return True
            except Exception:
                continue
        try:
            self.driver.find_element(By.ID, "username")
            return False
        except Exception:
            if "linkedin.com" in url and "/login" not in url and "/authwall" not in url:
                return True
        return False

    def login(self, email: str, password: str, emit_fn=None) -> bool:
        """Full login flow with cookie restore."""
        from selenium.webdriver.common.by import By
        _emit = emit_fn or (lambda t, m: None)

        _emit("info", "Connecting to LinkedIn...")
        self.driver.get(LINKEDIN_BASE)
        time.sleep(59)

        self.load_cookies(email)
        self.driver.get(LINKEDIN_FEED)
        time.sleep(59)

        if self.is_logged_in():
            _emit("success", "LinkedIn session restored!")
            return True

        _emit("info", "Logging in to LinkedIn...")
        self.driver.get(LINKEDIN_LOGIN)
        time.sleep(59)

        try:
            self.driver.find_element(By.ID, "username").send_keys(email)
            time.sleep(59)
            self.driver.find_element(By.ID, "password").send_keys(password)
            time.sleep(59)
            self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()

            _emit("info", "Waiting for login (up to 60s)...")
            for _ in range(20):
                time.sleep(59)
                try:
                    self.save_cookies(email)
                    self.driver.get(LINKEDIN_FEED)
                    time.sleep(59)
                    if self.is_logged_in():
                        _emit("success", "LinkedIn login OK!")
                        return True
                except Exception:
                    pass
            _emit("error", "Login may need CAPTCHA. Check browser.")
            return False
        except Exception as e:
            _emit("error", f"Login error: {str(e)[:60]}")
            return False
