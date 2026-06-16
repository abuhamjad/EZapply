# LinkedIn Bot — Automated Easy Apply via Selenium
import hashlib, math, os, pickle, random, time, queue
from typing import Optional, Dict, List
import constants

class LinkedinBot:
    ANSWERS_FILE = os.path.join(os.getcwd(), "user_answers.json")

    def __init__(self, config: Dict, event_queue: queue.Queue, resume_data: Dict = None, response_queue: queue.Queue = None):
        self.config = config
        self.event_queue = event_queue
        self.response_queue = response_queue or queue.Queue()
        self.resume_data = resume_data or {}
        self.driver = None
        self.running = False
        self.stats = {"jobs_found":0,"applied":0,"skipped":0,"blacklisted":0,"already_applied":0,"failed":0}
        self._user_answers = self._load_saved_answers()

    def _load_saved_answers(self):
        """Load previously saved user answers from disk."""
        import json
        try:
            if os.path.exists(self.ANSWERS_FILE):
                with open(self.ANSWERS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception:
            pass
        return {}

    def _save_answers(self):
        """Persist all user answers to disk for future sessions."""
        import json
        try:
            with open(self.ANSWERS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._user_answers, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def emit(self, etype, msg, data=None):
        self.event_queue.put({"type":etype,"message":msg,"data":data or {},"timestamp":time.strftime("%H:%M:%S")})

    def ask_user(self, field_name, job_title=""):
        """Ask user for missing field value. Checks saved answers first, only asks for new ones."""
        # Normalize key for matching
        cache_key = field_name.lower().strip()
        # Strip option lists from key for better matching
        # e.g. "Years of experience (options: 1, 2, 3)" → "years of experience"
        base_key = cache_key.split("(options")[0].strip() if "(options" in cache_key else cache_key

        # Check saved answers — exact match first, then fuzzy
        if base_key in self._user_answers:
            self.emit("info", f"💾 Auto-answered \"{field_name}\" from saved data")
            return self._user_answers[base_key]
        # Fuzzy match: check if any saved key is substring of this field or vice versa
        for saved_key, saved_val in self._user_answers.items():
            if saved_key in base_key or base_key in saved_key:
                self.emit("info", f"💾 Auto-answered \"{field_name}\" from saved data")
                return saved_val

        # Not found in saved answers — ask user
        prompt = f"📝 Bot needs your input for: \"{field_name}\""
        if job_title:
            prompt += f" (applying to: {job_title})"
        self.emit("question", prompt, {"field": field_name, "job": job_title})
        try:
            answer = self.response_queue.get(timeout=120)  # Wait 2 min max
            if answer == "__SKIP__":
                return ""
            # Save answer for this session AND future sessions
            self._user_answers[base_key] = answer
            self._save_answers()
            self.emit("info", f"✅ Saved answer for \"{field_name}\" (won't ask again)")
            return answer
        except queue.Empty:
            self.emit("warning", f"⏰ No response for \"{field_name}\", skipping...")
            return ""

    def setup_driver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        options = webdriver.ChromeOptions()
        for arg in ["--no-sandbox","--ignore-certificate-errors","--disable-extensions","--disable-gpu","--disable-dev-shm-usage","--start-maximized","--disable-blink-features=AutomationControlled","--incognito"]:
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
        except Exception:
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        try:
            from selenium_stealth import stealth
            stealth(self.driver, languages=["en-US","en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
        except ImportError: pass

    def get_hash(self, s): return hashlib.md5(s.encode("utf-8")).hexdigest()

    def load_cookies(self):
        d = os.path.join(os.getcwd(), "cookies"); os.makedirs(d, exist_ok=True)
        p = os.path.join(d, f"{self.get_hash(self.config['linkedin_email'])}.pkl")
        if os.path.exists(p):
            try:
                with open(p,"rb") as f: cookies = pickle.load(f)
                self.driver.delete_all_cookies()
                for c in cookies:
                    try: self.driver.add_cookie(c)
                    except: pass
            except: pass

    def save_cookies(self):
        d = os.path.join(os.getcwd(), "cookies"); os.makedirs(d, exist_ok=True)
        p = os.path.join(d, f"{self.get_hash(self.config['linkedin_email'])}.pkl")
        try:
            with open(p,"wb") as f: pickle.dump(self.driver.get_cookies(), f)
        except: pass

    def login(self):
        from selenium.webdriver.common.by import By
        self.emit("info","🔄 Connecting to LinkedIn...")
        self.driver.get(constants.LINKEDIN_BASE); time.sleep(3)
        self.load_cookies()
        self.driver.get(constants.LINKEDIN_FEED); time.sleep(5)
        if self._is_logged_in():
            self.emit("success","✅ LinkedIn session restored!"); return True
        self.emit("info","🔑 Logging into LinkedIn...")
        self.driver.get(constants.LINKEDIN_LOGIN); time.sleep(3)
        try:
            self.driver.find_element(By.ID,"username").send_keys(self.config["linkedin_email"]); time.sleep(1)
            self.driver.find_element(By.ID,"password").send_keys(self.config["linkedin_password"]); time.sleep(1)
            self.driver.find_element(By.XPATH,'//button[@type="submit"]').click()
            self.emit("info","⏳ Waiting for login (30s for CAPTCHA)..."); time.sleep(30)
            self.save_cookies()
            self.driver.get(constants.LINKEDIN_FEED); time.sleep(5)
            if self._is_logged_in():
                self.emit("success","✅ LinkedIn login OK!"); return True
            else:
                self.emit("error","❌ Login may need manual CAPTCHA. Check browser."); return False
        except Exception as e:
            self.emit("error",f"❌ Login error: {str(e)[:60]}"); return False

    def _is_logged_in(self):
        """Check if logged into LinkedIn using multiple methods."""
        from selenium.webdriver.common.by import By
        url = self.driver.current_url
        # Method 1: URL check — if on feed/home, we're logged in
        if "/feed" in url or "/mynetwork" in url or "/jobs" in url:
            if "/login" not in url and "/authwall" not in url:
                return True
        # Method 2: Check page title
        title = self.driver.title.lower()
        if "feed" in title or "linkedin" in title and "login" not in title and "sign" not in title:
            pass  # Could be logged in, check DOM too
        # Method 3: Try multiple selectors for logged-in state
        selectors = [
            "div.feed-identity-module",
            "div.global-nav__me",
            "img.global-nav__me-photo",
            "div[data-control-name='identity_welcome_message']",
            "a[href*='/me/']",
            "div.scaffold-layout",
            "nav.global-nav",
        ]
        for sel in selectors:
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, sel)
                if el: return True
            except: continue
        # Method 4: Check if login page elements are absent
        try:
            self.driver.find_element(By.ID, "username")
            return False  # Still on login page
        except:
            # No login form found and we're on linkedin.com
            if "linkedin.com" in url and "/login" not in url and "/authwall" not in url:
                return True
        return False

    def generate_search_urls(self):
        urls = []
        kws = self.config.get("keywords") or self.resume_data.get("search_keywords",["software engineer"])
        locs = self.config.get("location",["India"])
        for loc in locs:
            for kw in kws:
                u = f"{constants.LINKEDIN_JOBS_SEARCH}?f_AL=true&keywords={kw}"
                jtc = [constants.JOB_TYPES[j] for j in self.config.get("job_types",[]) if j in constants.JOB_TYPES]
                if jtc: u += "&f_JT=" + "%2C".join(jtc)
                rtc = [constants.REMOTE_TYPES[r] for r in self.config.get("remote",[]) if r in constants.REMOTE_TYPES]
                if rtc: u += "&f_WT=" + "%2C".join(rtc)
                u += f"&location={loc}"
                gid = constants.GEO_IDS.get(loc.lower(),"")
                if gid: u += f"&geoId={gid}"
                exc = [constants.EXPERIENCE_LEVELS[e] for e in self.config.get("experience_levels",[]) if e in constants.EXPERIENCE_LEVELS]
                if exc: u += "&f_E=" + "%2C".join(exc)
                dp = constants.DATE_POSTED.get(self.config.get("date_posted","Past Week"),"")
                if dp: u += f"&f_TPR={dp}"
                sc = constants.SORT_BY.get(self.config.get("sort_by","Recent"),"DD")
                u += f"&sortBy={sc}"
                urls.append(u)
        return urls

    def apply_to_jobs(self):
        from selenium.webdriver.common.by import By
        self.running = True
        urls = self.generate_search_urls()
        self.emit("info",f"🔍 Searching {len(urls)} URLs...")
        mx = self.config.get("max_applications",50)
        bl_co = [c.lower() for c in self.config.get("blacklist_companies",[])]
        bl_ti = [t.lower() for t in self.config.get("blacklist_titles",[])]
        dry = self.config.get("dry_run", False)
        for ui, url in enumerate(urls):
            if not self.running: break
            self.driver.get(url); time.sleep(random.uniform(2, constants.BOT_SPEED))
            try:
                tjt = self.driver.find_element(By.XPATH,"//small").text
                self.emit("info",f"📋 Found {tjt} — URL {ui+1}/{len(urls)}")
            except:
                self.emit("warning",f"⚠️ No jobs URL {ui+1}"); continue
            try:
                tc = int(tjt.split(" ")[0].replace(",","")) if " " in tjt else int(tjt.replace(",",""))
                tp = min(math.ceil(tc/constants.JOBS_PER_PAGE), 40)
            except: tp = 1
            for pg in range(tp):
                if not self.running or self.stats["applied"]>=mx: break
                self.driver.get(url+f"&start={constants.JOBS_PER_PAGE*pg}"); time.sleep(random.uniform(2, constants.BOT_SPEED))
                offers = self.driver.find_elements(By.XPATH,"//li[@data-occludable-job-id]")
                oids = []
                for o in offers:
                    try:
                        oid = o.get_attribute("data-occludable-job-id")
                        if oid: oids.append(int(oid.split(":")[-1]))
                    except: continue
                try:
                    offers2 = self.driver.find_elements(By.XPATH,"//li[@data-occludable-job-id]")
                    aids = []
                    for o in offers2:
                        try:
                            if o.find_elements(By.XPATH,".//*[contains(text(),'Applied')]"):
                                oid = o.get_attribute("data-occludable-job-id")
                                if oid: aids.append(int(oid.split(":")[-1]))
                        except: continue
                    oids = [j for j in oids if j not in aids]
                except: pass
                for jid in oids:
                    if not self.running or self.stats["applied"]>=mx: break
                    ju = f"https://www.linkedin.com/jobs/view/{jid}"
                    self.driver.get(ju); time.sleep(random.uniform(2, constants.BOT_SPEED))
                    self.stats["jobs_found"] += 1
                    jt = jc = ""
                    try: jt = self.driver.find_element(By.XPATH,"//h1[contains(@class,'job-title')]").text.strip()
                    except:
                        try: jt = self.driver.find_element(By.CSS_SELECTOR,"h1.t-24").text.strip()
                        except: jt = f"Job #{jid}"
                    try: jc = self.driver.find_element(By.XPATH,"//div[contains(@class,'job-details-jobs')]//div").text.split("\n")[0].strip()
                    except: jc = "Unknown"
                    if any(b in jt.lower() for b in bl_ti): self.stats["blacklisted"]+=1; self.emit("warning",f"🚫 Blacklisted: {jt}"); continue
                    if any(b in jc.lower() for b in bl_co): self.stats["blacklisted"]+=1; self.emit("warning",f"🚫 Blacklisted: {jc}"); continue
                    eab = None
                    try:
                        time.sleep(1)
                        eab = self.driver.find_element(By.XPATH,"//div[contains(@class,'jobs-apply-button--top-card')]//button[contains(@class,'jobs-apply-button')]")
                    except: pass
                    if not eab: self.stats["already_applied"]+=1; self.emit("info",f"✔️ Already applied: {jt}"); continue
                    if dry: self.stats["applied"]+=1; self.emit("success",f"🧪 DRY RUN: {jt} @ {jc}"); self.emit("stats","📊",self.stats.copy()); continue
                    try:
                        eab.click(); time.sleep(random.uniform(1, constants.BOT_SPEED))
                        try:
                            cb = self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Continue to next step']")
                            if cb.is_displayed(): cb.click(); time.sleep(1)
                        except: pass
                        self._choose_resume(); self._fill_all_fields(jt)
                        try:
                            self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Submit application']").click()
                            time.sleep(1); self.stats["applied"]+=1; self.emit("success",f"🎉 Applied: {jt} @ {jc}")
                        except:
                            r = self._multi_step(jt, jc)
                            if "applied" in r.lower(): self.stats["applied"]+=1
                            else: self.stats["failed"]+=1
                    except Exception as e: self.stats["failed"]+=1; self.emit("error",f"❌ Failed: {jt} — {str(e)[:50]}")
                    self.emit("stats","📊",self.stats.copy())
        self.running = False
        self.emit("complete",f"✅ Done! Applied: {self.stats['applied']}",self.stats.copy())

    def _choose_resume(self):
        from selenium.webdriver.common.by import By
        try:
            self.driver.find_element(By.CLASS_NAME,"jobs-document-upload__title--is-required")
            rs = self.driver.find_elements(By.XPATH,"//div[contains(@class,'ui-attachment--pdf')]")
            for r in rs:
                if r.get_attribute("aria-label")=="Select this resume": r.click(); break
        except: pass
        # Also try file upload if available and resume path exists
        try:
            upload = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            rpath = self.config.get("resume_path","")
            if upload and rpath and os.path.exists(rpath):
                upload.send_keys(rpath)
                time.sleep(2)
        except: pass

    def _fill_all_fields(self, job_title=""):
        """Fill all form fields using scraped resume data. Ask user for missing required ones."""
        from selenium.webdriver.common.by import By
        rd = self.resume_data
        phone = rd.get("phone","")
        email = rd.get("email","")
        name = rd.get("name","")
        city = rd.get("current_location","")
        linkedin_url = rd.get("linkedin_url","")
        first_name = name.split()[0] if name else ""
        last_name = " ".join(name.split()[1:]) if name and len(name.split())>1 else ""

        # Map of label keywords → values to fill
        field_map = {
            "phone": phone, "mobile": phone, "cell": phone,
            "email": email, "e-mail": email,
            "first name": first_name, "given name": first_name,
            "last name": last_name, "surname": last_name, "family name": last_name,
            "full name": name, "city": city, "location": city,
            "current location": city, "linkedin": linkedin_url,
        }

        # Fill input[type=tel] fields (phone)
        if phone:
            try:
                for inp in self.driver.find_elements(By.CSS_SELECTOR, "input[type='tel']"):
                    if inp.is_displayed() and not inp.get_attribute("value"):
                        inp.clear(); inp.send_keys(phone); break
            except: pass

        # Fill text inputs by matching labels
        try:
            labels = self.driver.find_elements(By.CSS_SELECTOR, "label")
            for label in labels:
                try:
                    label_text = label.text.strip().lower()
                    if not label_text: continue
                    fill_value = ""
                    for key, val in field_map.items():
                        if key in label_text and val:
                            fill_value = val; break
                    if not fill_value: continue
                    for_id = label.get_attribute("for")
                    inp = None
                    if for_id:
                        try: inp = self.driver.find_element(By.ID, for_id)
                        except: pass
                    if not inp:
                        try:
                            parent = label.find_element(By.XPATH, "..")
                            inp = parent.find_element(By.CSS_SELECTOR, "input, select, textarea")
                        except: pass
                    if inp and inp.is_displayed():
                        tag = inp.tag_name.lower()
                        current = inp.get_attribute("value") or ""
                        if tag in ("input","textarea") and not current:
                            inp.clear(); inp.send_keys(fill_value)
                        elif tag == "select":
                            from selenium.webdriver.support.ui import Select
                            sel = Select(inp)
                            for opt in sel.options:
                                if fill_value.lower() in opt.text.lower():
                                    sel.select_by_visible_text(opt.text); break
                except: continue
        except: pass

        # Fill remaining by placeholder/name/id matching
        try:
            all_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[type='tel'], input:not([type])")
            for inp in all_inputs:
                try:
                    if not inp.is_displayed(): continue
                    current = inp.get_attribute("value") or ""
                    if current: continue
                    attrs = " ".join([
                        inp.get_attribute("placeholder") or "",
                        inp.get_attribute("name") or "",
                        inp.get_attribute("id") or "",
                        inp.get_attribute("aria-label") or "",
                    ]).lower()
                    for key, val in field_map.items():
                        if key in attrs and val:
                            inp.clear(); inp.send_keys(val); break
                except: continue
        except: pass

        # --- Detect remaining unfilled REQUIRED fields and ask user ---
        self._ask_for_missing_fields(job_title)

    def _ask_for_missing_fields(self, job_title=""):
        """Find empty required fields bot couldn't fill, ask user."""
        from selenium.webdriver.common.by import By
        try:
            # Check for required text/tel/email inputs that are still empty
            all_inputs = self.driver.find_elements(By.CSS_SELECTOR,
                "input[required], textarea[required], input[aria-required='true'], textarea[aria-required='true']"
            )
            for inp in all_inputs:
                try:
                    if not inp.is_displayed(): continue
                    current = (inp.get_attribute("value") or "").strip()
                    if current: continue
                    # Get field label
                    field_label = self._get_field_label(inp)
                    if not field_label:
                        field_label = inp.get_attribute("placeholder") or inp.get_attribute("aria-label") or "Unknown field"
                    answer = self.ask_user(field_label, job_title)
                    if answer:
                        inp.clear(); inp.send_keys(answer)
                except: continue

            # Check for required selects with no selection
            selects = self.driver.find_elements(By.CSS_SELECTOR,
                "select[required], select[aria-required='true']"
            )
            for sel_el in selects:
                try:
                    if not sel_el.is_displayed(): continue
                    from selenium.webdriver.support.ui import Select
                    sel = Select(sel_el)
                    selected = sel.first_selected_option.text.strip().lower()
                    if selected and selected not in ("select", "choose", "--", "select an option", ""):
                        continue
                    field_label = self._get_field_label(sel_el)
                    if not field_label: field_label = "Dropdown selection"
                    # Show options to user
                    options = [o.text.strip() for o in sel.options if o.text.strip() and o.text.strip().lower() not in ("select","--","select an option")]
                    answer = self.ask_user(f"{field_label} (options: {', '.join(options[:8])})", job_title)
                    if answer:
                        for opt in sel.options:
                            if answer.lower() in opt.text.lower():
                                sel.select_by_visible_text(opt.text); break
                except: continue

            # Check for unanswered radio button groups
            fieldsets = self.driver.find_elements(By.CSS_SELECTOR, "fieldset[data-test-form-builder-radio-button-form-component]")
            for fs in fieldsets:
                try:
                    if not fs.is_displayed(): continue
                    # Check if any radio is selected
                    checked = fs.find_elements(By.CSS_SELECTOR, "input[type='radio']:checked")
                    if checked: continue
                    legend = ""
                    try: legend = fs.find_element(By.CSS_SELECTOR, "legend, span.fb-dash-form-element__label").text.strip()
                    except: pass
                    if not legend: continue
                    radios = fs.find_elements(By.CSS_SELECTOR, "label")
                    radio_options = [r.text.strip() for r in radios if r.text.strip()]
                    answer = self.ask_user(f"{legend} (options: {', '.join(radio_options[:6])})", job_title)
                    if answer:
                        for r in radios:
                            if answer.lower() in r.text.lower():
                                r.click(); break
                except: continue
        except: pass

    def _get_field_label(self, element):
        """Get human-readable label for a form element."""
        from selenium.webdriver.common.by import By
        try:
            el_id = element.get_attribute("id")
            if el_id:
                try:
                    label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{el_id}']")
                    if label.text.strip(): return label.text.strip()
                except: pass
            try:
                parent = element.find_element(By.XPATH, "..")
                label = parent.find_element(By.CSS_SELECTOR, "label, span.fb-dash-form-element__label")
                if label.text.strip(): return label.text.strip()
            except: pass
            try:
                parent2 = element.find_element(By.XPATH, "../..")
                label = parent2.find_element(By.CSS_SELECTOR, "label, span.fb-dash-form-element__label")
                if label.text.strip(): return label.text.strip()
            except: pass
        except: pass
        return ""

    def _multi_step(self, title, company):
        from selenium.webdriver.common.by import By
        try:
            for step in range(7):
                self._choose_resume()
                self._fill_all_fields(title)
                time.sleep(0.5)
                # Try continue
                try:
                    btn = self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Continue to next step']")
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click(); time.sleep(1.5)
                    else: break
                except: break
            # Final review
            self._choose_resume()
            self._fill_all_fields(title)
            try: self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Review your application']").click(); time.sleep(1)
            except: pass
            if not self.config.get("follow_companies"):
                try: self.driver.find_element(By.CSS_SELECTOR,"label[for='follow-company-checkbox']").click()
                except: pass
            self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Submit application']").click(); time.sleep(1)
            self.emit("success",f"🎉 Applied (multi): {title} @ {company}"); return "Applied"
        except Exception as e:
            self.emit("error",f"❌ Multi-step fail: {title}"); 
            try: self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Dismiss']").click()
            except: pass
            return "Failed"

    def stop(self): self.running = False; self.emit("info","⏹️ Stopping...")
    def cleanup(self):
        if self.driver:
            try: self.driver.quit()
            except: pass
