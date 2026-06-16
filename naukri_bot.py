# Naukri.com Bot — Automated job apply via Selenium
import hashlib, os, pickle, random, time, queue
from typing import Dict, List
import constants

class NaukriBot:
    def __init__(self, config: Dict, event_queue: queue.Queue, resume_data: Dict = None):
        self.config = config
        self.event_queue = event_queue
        self.resume_data = resume_data or {}
        self.driver = None
        self.running = False
        self.stats = {"jobs_found":0,"applied":0,"skipped":0,"failed":0,"already_applied":0}

    def emit(self, etype, msg, data=None):
        self.event_queue.put({"type":etype,"message":msg,"data":data or {},"timestamp":time.strftime("%H:%M:%S")})

    def setup_driver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        options = webdriver.ChromeOptions()
        for arg in ["--no-sandbox","--ignore-certificate-errors","--disable-extensions","--disable-gpu","--disable-dev-shm-usage","--start-maximized","--disable-blink-features=AutomationControlled"]:
            options.add_argument(arg)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if self.config.get("headless"): options.add_argument("--headless")
        try:
            ci = ChromeDriverManager().install()
            folder = os.path.dirname(ci)
            cp = os.path.join(folder, "chromedriver.exe")
            if not os.path.exists(cp): cp = ci
            self.driver = webdriver.Chrome(service=ChromeService(cp), options=options)
        except:
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        try:
            from selenium_stealth import stealth
            stealth(self.driver, languages=["en-US","en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
        except: pass

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
        kws = self.config.get("keywords") or self.resume_data.get("search_keywords",["software engineer"])
        loc = self.config.get("location",["India"])[0] if self.config.get("location") else "India"
        mx = self.config.get("max_applications",50)
        dry = self.config.get("dry_run", False)
        for kw in kws:
            if not self.running or self.stats["applied"]>=mx: break
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
                    # Find apply button
                    applied = False
                    for sel in ["button#apply-button","button.apply-button","button[id*='apply']","button[class*='apply']","a[class*='apply']"]:
                        try:
                            btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                            if btn.is_displayed() and btn.is_enabled():
                                btn.click(); time.sleep(2)
                                self.stats["applied"]+=1; applied = True
                                self.emit("success",f"🎉 Naukri applied: {jt}"); break
                        except: continue
                    if not applied:
                        # Check if already applied
                        try:
                            page = self.driver.page_source.lower()
                            if "already applied" in page or "applied" in page:
                                self.stats["already_applied"]+=1; self.emit("info",f"✔️ Already applied: {jt}")
                            else:
                                self.stats["failed"]+=1; self.emit("warning",f"⚠️ No apply btn: {jt}")
                        except: self.stats["failed"]+=1
                except Exception as e:
                    self.stats["failed"]+=1; self.emit("error",f"❌ Naukri error: {str(e)[:50]}")
                self.emit("stats","📊",self.stats.copy())
        self.running = False
        self.emit("complete",f"✅ Naukri done! Applied: {self.stats['applied']}",self.stats.copy())

    def stop(self): self.running = False; self.emit("info","⏹️ Naukri stopping...")
    def cleanup(self):
        if self.driver:
            try: self.driver.quit()
            except: pass
