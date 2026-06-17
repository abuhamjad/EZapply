# ============================================================
# Application Configuration
# ============================================================
import os
import sys
from pathlib import Path


def _get_app_data_dir() -> Path:
    """Cross-platform application data directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    app_dir = base / "JobPilotAI"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


# Paths
APP_DATA_DIR = _get_app_data_dir()
DATABASE_PATH = APP_DATA_DIR / "jobpilot.db"
RESUMES_DIR = APP_DATA_DIR / "resumes"
COOKIES_DIR = APP_DATA_DIR / "cookies"
LOGS_DIR = APP_DATA_DIR / "logs"
ENCRYPTION_KEY_FILE = APP_DATA_DIR / ".keyfile"

# Ensure directories exist
for d in (RESUMES_DIR, COOKIES_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Server
API_HOST = "127.0.0.1"
API_PORT = 8420

# Bot defaults
BOT_SPEED_SLOW = 5
BOT_SPEED_MEDIUM = 3
BOT_SPEED_FAST = 2
JOBS_PER_PAGE = 25
MAX_APPLICATION_STEPS = 10

# AI defaults
BEDROCK_DEFAULT_REGION = "us-east-1"
BEDROCK_DEFAULT_MODEL = "anthropic.claude-3-5-sonnet-20241022-v2:0"
AI_MAX_RETRIES = 3
AI_RATE_LIMIT_RPM = 10
AI_REQUEST_TIMEOUT = 30

# Platform URLs
LINKEDIN_BASE = "https://www.linkedin.com"
LINKEDIN_LOGIN = "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin"
LINKEDIN_FEED = "https://www.linkedin.com/feed"
LINKEDIN_JOBS_SEARCH = "https://www.linkedin.com/jobs/search/"

NAUKRI_BASE = "https://www.naukri.com"
NAUKRI_LOGIN = "https://www.naukri.com/nlogin/login"

# LinkedIn filter codes
GEO_IDS = {
    "asia": "102393603", "europe": "100506914",
    "northamerica": "102221843", "southamerica": "104514572",
    "australia": "101452733", "africa": "103537801",
    "india": "102713980", "worldwide": "",
}
EXPERIENCE_LEVELS = {
    "Internship": "1", "Entry level": "2", "Associate": "3",
    "Mid-Senior level": "4", "Director": "5", "Executive": "6",
}
JOB_TYPES = {
    "Full-time": "F", "Part-time": "P", "Contract": "C",
    "Temporary": "T", "Volunteer": "V", "Internship": "I", "Other": "O",
}
REMOTE_TYPES = {"On-site": "1", "Remote": "2", "Hybrid": "3"}
DATE_POSTED = {
    "Any Time": "", "Past Month": "r2592000",
    "Past Week": "r604800", "Past 24 hours": "r86400",
}
SORT_BY = {"Recent": "DD", "Relevant": "R"}
