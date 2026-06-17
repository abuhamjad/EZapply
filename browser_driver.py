# ============================================================
# Universal Browser Driver — Auto-detects system browser
# Supports: Edge, Chrome, Firefox (in detection order)
# ============================================================
import os
import shutil
import subprocess
import sys


def _is_browser_installed(name):
    """Check if browser executable exists on system."""
    if sys.platform == "win32":
        paths = {
            "edge": [
                os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
            ],
            "chrome": [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            ],
            "firefox": [
                os.path.expandvars(r"%ProgramFiles%\Mozilla Firefox\firefox.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"),
            ],
        }
        for p in paths.get(name, []):
            if os.path.exists(p):
                return True
        return False
    else:
        # Linux/Mac — check PATH
        cmds = {"edge": "microsoft-edge", "chrome": "google-chrome", "firefox": "firefox"}
        return shutil.which(cmds.get(name, "")) is not None


def detect_browser():
    """Detect best available browser. Returns: 'edge', 'chrome', or 'firefox'."""
    # Edge ships with Windows — try first
    for browser in ["edge", "chrome", "firefox"]:
        if _is_browser_installed(browser):
            return browser
    # Fallback: try Chrome anyway (webdriver-manager will download it)
    return "chrome"


def create_driver(headless=False):
    """Create Selenium WebDriver for best available browser.
    
    Returns (driver, browser_name) tuple.
    """
    from selenium import webdriver

    browser = detect_browser()

    stealth_args = [
        "--no-sandbox",
        "--ignore-certificate-errors",
        "--disable-extensions",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--start-maximized",
        "--disable-blink-features=AutomationControlled",
    ]

    driver = None

    if browser == "edge":
        driver = _create_edge_driver(webdriver, stealth_args, headless)
    elif browser == "chrome":
        driver = _create_chrome_driver(webdriver, stealth_args, headless)
    elif browser == "firefox":
        driver = _create_firefox_driver(webdriver, stealth_args, headless)

    # Fallback chain: edge → chrome → firefox
    if driver is None and browser != "edge":
        try:
            driver = _create_edge_driver(webdriver, stealth_args, headless)
            browser = "edge"
        except Exception:
            pass
    if driver is None and browser != "chrome":
        try:
            driver = _create_chrome_driver(webdriver, stealth_args, headless)
            browser = "chrome"
        except Exception:
            pass
    if driver is None and browser != "firefox":
        try:
            driver = _create_firefox_driver(webdriver, stealth_args, headless)
            browser = "firefox"
        except Exception:
            pass

    if driver is None:
        raise RuntimeError(
            "No supported browser found. Install Edge, Chrome, or Firefox."
        )

    # Apply stealth (Chrome/Edge only)
    if browser in ("edge", "chrome"):
        try:
            from selenium_stealth import stealth
            stealth(
                driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
        except ImportError:
            pass

    return driver, browser


def _create_edge_driver(webdriver, stealth_args, headless):
    """Create Microsoft Edge WebDriver."""
    try:
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager.microsoft import EdgeChromiumDriverManager

        options = webdriver.EdgeOptions()
        for arg in stealth_args:
            options.add_argument(arg)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if headless:
            options.add_argument("--headless")
        try:
            ei = EdgeChromiumDriverManager().install()
            folder = os.path.dirname(ei)
            ep = os.path.join(folder, "msedgedriver.exe")
            if not os.path.exists(ep):
                ep = ei
            return webdriver.Edge(service=EdgeService(ep), options=options)
        except Exception:
            return webdriver.Edge(
                service=EdgeService(EdgeChromiumDriverManager().install()),
                options=options,
            )
    except Exception:
        return None


def _create_chrome_driver(webdriver, stealth_args, headless):
    """Create Google Chrome WebDriver."""
    try:
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager

        options = webdriver.ChromeOptions()
        for arg in stealth_args:
            options.add_argument(arg)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if headless:
            options.add_argument("--headless")
        try:
            ci = ChromeDriverManager().install()
            folder = os.path.dirname(ci)
            cp = os.path.join(folder, "chromedriver.exe")
            if not os.path.exists(cp):
                cp = ci
            return webdriver.Chrome(service=ChromeService(cp), options=options)
        except Exception:
            return webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options,
            )
    except Exception:
        return None


def _create_firefox_driver(webdriver, stealth_args, headless):
    """Create Mozilla Firefox WebDriver."""
    try:
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager

        options = webdriver.FirefoxOptions()
        # Firefox uses different args
        if headless:
            options.add_argument("--headless")
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        try:
            return webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=options,
            )
        except Exception:
            return webdriver.Firefox(options=options)
    except Exception:
        return None
