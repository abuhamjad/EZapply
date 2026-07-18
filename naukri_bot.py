import hashlib, os, pickle, random, time, queue, threading
from typing import Dict, List
import constants

class NaukriBot:
    def __init__(self, config: Dict, event_queue: queue.Queue, resume_data: Dict = None):
        self.config = config
        self.event_queue = event_queue
        self.resume_data = resume_data or {}
        self.driver = None
        self.running = False
        self._pause_event = threading.Event()
        self.stats = {"jobs_found":0,"applied":0,"skipped":0,"failed":0,"already_applied":0}

    def emit(self, etype, msg, data=None):
        self.event_queue.put({"type":etype,"message":msg,"data":data or {},"timestamp":time.strftime("%H:%M:%S")})

    def pause(self):
        self._pause_event.set()
        self.emit("info", "Automation paused at a safe point")

    def resume(self):
        self._pause_event.clear()
        self.emit("info", "Automation resumed")

    def wait_if_paused(self):
        while self.running and self._pause_event.is_set():
            time.sleep(0.25)

    def setup_driver(self):
        from browser_driver import create_driver
        self.driver, browser_name = create_driver(headless=self.config.get("headless", False))
        self.emit("info", f"🌐 Using {browser_name.title()} browser")

    def get_hash(self, s): return hashlib.md5(s.encode("utf-8")).hexdigest()

    def load_cookies(self):
        d = os.path.join(os.getcwd(),"cookies"); os.makedirs(d,exist_ok=True)
        p = os.path.join(d, f"naukri_{self.get_hash(self.config.get('naukri_email',''))}.pkl")
        if os.path.exists(p):
            try:
                with open(p,"rb") as f: cookies = pickle.load(f)
                self.driver.delete_all_cookies()
                for c in cookies:
                    try: self.driver.add_cookie(c)
                    except: pass
            except: pass

    def save_cookies(self):
        d = os.path.join(os.getcwd(),"cookies"); os.makedirs(d,exist_ok=True)
        p = os.path.join(d, f"naukri_{self.get_hash(self.config.get('naukri_email',''))}.pkl")
        try:
            with open(p,"wb") as f: pickle.dump(self.driver.get_cookies(), f)
        except: pass

    def _find_element_multi(self, selectors, by_type=None):
        """Try multiple selectors, return first found element."""
        from selenium.webdriver.common.by import By
        by = by_type or By.CSS_SELECTOR
        for sel in selectors:
            try:
                el = self.driver.find_element(by, sel)
                if el and el.is_displayed(): return el
            except: continue
        return None

    def _is_logged_in(self):
        """Check if logged into Naukri using multiple methods."""
        from selenium.webdriver.common.by import By
        url = self.driver.current_url.lower()
        # Check URL
        if "nlogin" in url or "login" in url:
            return False
        # Check for logged-in indicators
        indicators = [
            "div.nI-gNb-drawer__hamburger",
            "a.nI-gNb-header__userdp",
            "div.user-info",
            "a[href*='myprofile']",
            "div.nI-gNb-sb__icon",
            "span.nI-gNb-header__userName",
            "div[class*='user-dp']",
            "a[title='View Profile']",
        ]
        for sel in indicators:
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, sel)
                if el: return True
            except: continue
        # Check if login form is absent
        login_fields = ["#usernameField", "#passwordField", "input[placeholder*='Enter']", "input[type='email']"]
        for sel in login_fields:
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, sel)
                if el and el.is_displayed(): return False
            except: continue
        # If on naukri.com and no login form visible, likely logged in
        if "naukri.com" in url:
            return True
        return False

    def login(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        self.emit("info","🔄 Connecting to Naukri.com...")
        self.driver.get(constants.NAUKRI_BASE); time.sleep(3)
        self.load_cookies()
        self.driver.get(constants.NAUKRI_BASE); time.sleep(4)

        if self._is_logged_in():
            self.emit("success","✅ Naukri session restored!"); return True

        self.emit("info","🔑 Logging into Naukri...")
        self.driver.get(constants.NAUKRI_LOGIN); time.sleep(5)

        email = self.config.get("naukri_email","")
        password = self.config.get("naukri_password","")

        # Try multiple selectors for username field
        username_selectors = [
            "input#usernameField",
            "input[placeholder*='Enter your active Email ID']",
            "input[placeholder*='Email']",
            "input[placeholder*='email']",
            "input[type='email']",
            "input[name='username']",
            "input[id*='username']",
            "input[id*='email']",
            "div.form-row input:first-child",
        ]
        user_el = self._find_element_multi(username_selectors)

        if not user_el:
            # Try XPath as last resort
            xpath_selectors = [
                "//input[@type='text' and contains(@placeholder,'Email')]",
                "//input[@type='email']",
                "//input[contains(@id,'user')]",
                "//input[contains(@class,'user')]",
            ]
            user_el = self._find_element_multi(xpath_selectors, By.XPATH)

        if not user_el:
            self.emit("error","❌ Cannot find Naukri email field. UI may have changed.")
            # Take a screenshot for debug
            try: self.driver.save_screenshot(os.path.join(os.getcwd(),"naukri_login_debug.png"))
            except: pass
            return False

        # Enter email
        try:
            user_el.clear()
            user_el.send_keys(email)
            time.sleep(1)
        except Exception as e:
            self.emit("error",f"❌ Cannot type email: {str(e)[:50]}"); return False

        # Try multiple selectors for password field
        password_selectors = [
            "input#passwordField",
            "input[placeholder*='Enter your password']",
            "input[placeholder*='Password']",
            "input[placeholder*='password']",
            "input[type='password']",
            "input[name='password']",
            "input[id*='password']",
        ]
        pass_el = self._find_element_multi(password_selectors)

        if not pass_el:
            self.emit("error","❌ Cannot find Naukri password field.")
            return False

        # Enter password
        try:
            pass_el.clear()
            pass_el.send_keys(password)
            time.sleep(1)
        except Exception as e:
            self.emit("error",f"❌ Cannot type password: {str(e)[:50]}"); return False

        # Click login button
        login_btn_selectors = [
            "button[type='submit']",
            "button.loginButton",
            "button[class*='login']",
            "button[class*='Login']",
            "button[class*='submit']",
            "input[type='submit']",
        ]
        login_btn = self._find_element_multi(login_btn_selectors)

        if not login_btn:
            login_btn = self._find_element_multi([
                "//button[@type='submit']",
                "//button[contains(text(),'Login')]",
                "//button[contains(text(),'login')]",
                "//button[contains(text(),'Sign')]",
            ], By.XPATH)

        if login_btn:
            try:
                login_btn.click()
            except:
                pass_el.send_keys(Keys.RETURN)
        else:
            pass_el.send_keys(Keys.RETURN)

        self.emit("info","⏳ Waiting for Naukri login (15s)..."); time.sleep(15)
        self.save_cookies()

        if self._is_logged_in():
            self.emit("success","✅ Naukri login OK!"); return True
        else:
            self.emit("error","❌ Naukri login failed. Check credentials/CAPTCHA."); return False

    def apply_to_jobs(self):
        from selenium.webdriver.common.by import By
        self.running = True
        kws = self.config.get("keywords") or self.resume_data.get("search_keywords", [])
        loc = self.config.get("location", [""])[0] if self.config.get("location") else ""
        mx = self.config.get("max_applications",50)
        dry = self.config.get("dry_run", False)
        for kw in kws:
            if not self.running or self.stats["applied"]>=mx: break
            self.wait_if_paused()
            search_url = f"https://www.naukri.com/{kw.replace(' ','-')}-jobs-in-{loc.lower().replace(' ','-')}"
            self.emit("info",f"🔍 Naukri: searching '{kw}' in {loc}")
            self.driver.get(search_url); time.sleep(random.uniform(3,5))
            # Get job cards
            try:
                cards = self.driver.find_elements(By.CSS_SELECTOR, "article.jobTuple, div.srp-jobtuple-wrapper, div.cust-job-tuple")
                if not cards:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, "div.jobTupleHeader, a.title")
                self.emit("info",f"📋 Found {len(cards)} Naukri jobs for '{kw}'")
            except:
                self.emit("warning",f"⚠️ No Naukri jobs for '{kw}'"); continue
            links = []
            for card in cards[:20]:
                try:
                    a = card.find_element(By.CSS_SELECTOR, "a.title, a[class*='title']")
                    href = a.get_attribute("href")
                    if href: links.append(href)
                except:
                    try:
                        href = card.find_element(By.TAG_NAME,"a").get_attribute("href")
                        if href: links.append(href)
                    except: continue
            for link in links:
                if not self.running or self.stats["applied"]>=mx: break
                self.wait_if_paused()
                try:
                    self.driver.get(link); time.sleep(random.uniform(2,4))
                    self.stats["jobs_found"] += 1
                    jt = ""
                    try: jt = self.driver.find_element(By.CSS_SELECTOR,"h1.jd-header-title, h1.styles_jd-header-title__rZwM1").text.strip()
                    except:
                        try: jt = self.driver.find_element(By.TAG_NAME,"h1").text.strip()
                        except: jt = "Naukri Job"
                    if dry:
                        self.stats["applied"]+=1; self.emit("success",f"🧪 DRY RUN Naukri: {jt}")
                        self.emit("stats","📊",self.stats.copy()); continue

                    # Check for "Already Applied" badge specifically
                    already = False
                    already_selectors = [
                        "div.already-applied",
                        "span.already-applied",
                        "div[class*='already-applied']",
                        "span[class*='already-applied']",
                        "div.applied-msg",
                    ]
                    for sel in already_selectors:
                        try:
                            el = self.driver.find_element(By.CSS_SELECTOR, sel)
                            if el and el.is_displayed():
                                already = True; break
                        except: continue
                    if already:
                        self.stats["already_applied"]+=1
                        self.emit("info",f"✔️ Already applied: {jt}")
                        self.emit("stats","📊",self.stats.copy()); continue

                    # Find apply button — multiple selectors
                    applied = False
                    apply_selectors = [
                        "button#apply-button",
                        "button.apply-button",
                        "button[id*='apply']",
                        "button[class*='apply']",
                        "button[id='apply-btn']",
                        "button.styles_apply-button",
                        "div.apply-button-container button",
                    ]
                    # Track main window
                    main_window = self.driver.current_window_handle
                    for sel in apply_selectors:
                        try:
                            btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                            if btn.is_displayed() and btn.is_enabled():
                                btn_text = btn.text.strip().lower()
                                # Skip "already applied" buttons
                                if "already" in btn_text:
                                    already = True; break
                                btn.click(); time.sleep(3)
                                # Handle new tab opened by apply
                                handles = self.driver.window_handles
                                if len(handles) > 1:
                                    # New tab = external company site. Not a real Naukri apply.
                                    new_tab = None
                                    for h in handles:
                                        if h != main_window:
                                            new_tab = h; break
                                    if new_tab:
                                        self.driver.switch_to.window(new_tab)
                                        new_url = self.driver.current_url.lower()
                                        time.sleep(1)
                                        self.driver.close()
                                        self.driver.switch_to.window(main_window)
                                        if "naukri.com" not in new_url:
                                            # External redirect — skip, don't count
                                            self.stats["skipped"]+=1
                                            self.emit("info",f"↗️ External apply (skipped): {jt}")
                                            break
                                # Check if apply dialog appeared (Naukri chatbot apply)
                                time.sleep(1)
                                # Try to upload resume if upload field exists
                                try:
                                    upload = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                                    rpath = self.config.get("resume_path","")
                                    if upload and rpath and os.path.exists(rpath):
                                        upload.send_keys(rpath)
                                        time.sleep(2)
                                except: pass
                                # Try submitting any final apply/submit button in dialog
                                try:
                                    submit_selectors = [
                                        "button[type='submit']",
                                        "button.chatbot_submit",
                                        "button[class*='submit']",
                                        "button[class*='Submit']",
                                    ]
                                    for sub_sel in submit_selectors:
                                        try:
                                            sub_btn = self.driver.find_element(By.CSS_SELECTOR, sub_sel)
                                            if sub_btn.is_displayed() and sub_btn.is_enabled():
                                                sub_btn.click(); time.sleep(1); break
                                        except: continue
                                except: pass
                                self.stats["applied"]+=1; applied = True
                                self.emit("success",f"🎉 Naukri applied: {jt}"); break
                        except: continue

                    if already:
                        self.stats["already_applied"]+=1
                        self.emit("info",f"✔️ Already applied: {jt}")
                    elif not applied:
                        # XPath fallback — only for buttons, not anchor links (which are usually external)
                        try:
                            btn = self.driver.find_element(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'apply')]")
                            if btn.is_displayed() and btn.is_enabled():
                                btn.click(); time.sleep(3)
                                handles = self.driver.window_handles
                                if len(handles) > 1:
                                    for h in handles:
                                        if h != main_window:
                                            self.driver.switch_to.window(h)
                                            self.driver.close()
                                    self.driver.switch_to.window(main_window)
                                    self.stats["skipped"]+=1
                                    self.emit("info",f"↗️ External apply (skipped): {jt}")
                                else:
                                    self.stats["applied"]+=1; applied = True
                                    self.emit("success",f"🎉 Naukri applied: {jt}")
                        except: pass
                        if not applied:
                            self.stats["skipped"]+=1; self.emit("info",f"⏭️ No apply btn: {jt}")
                except Exception as e:
                    self.stats["failed"]+=1; self.emit("error",f"❌ Naukri error: {str(e)[:50]}")
                self.emit("stats","📊",self.stats.copy())
        self.running = False
        self.emit("complete",f"✅ Naukri done! Applied: {self.stats['applied']}",self.stats.copy())

    def stop(self): self.running = False; self._pause_event.clear(); self.emit("info","⏹️ Naukri stopping...")
    def cleanup(self):
        if self.driver:
            try: self.driver.quit()
            except: pass
