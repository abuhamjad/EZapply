# ============================================================
# Job Apply Bot — Constants & Configuration Defaults
# ============================================================
import os

# Platform URLs
LINKEDIN_BASE = "https://www.linkedin.com"
LINKEDIN_LOGIN = "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin"
LINKEDIN_FEED = "https://www.linkedin.com/feed"
LINKEDIN_JOBS_SEARCH = "https://www.linkedin.com/jobs/search/"

NAUKRI_BASE = "https://www.naukri.com"
NAUKRI_LOGIN = "https://www.naukri.com/nlogin/login"
NAUKRI_JOBS_SEARCH = "https://www.naukri.com/jobapi/v3/search"

# Selenium speed presets (seconds)
SPEED_FAST = 2
SPEED_MEDIUM = 3
SPEED_SLOW = 5
BOT_SPEED = SPEED_SLOW

# Pagination
JOBS_PER_PAGE = 25

# LinkedIn geo IDs
GEO_IDS = {
    "asia": "102393603",
    "europe": "100506914",
    "northamerica": "102221843",
    "southamerica": "104514572",
    "australia": "101452733",
    "africa": "103537801",
    "india": "102713980",
    "worldwide": "",
}

# Experience level codes (LinkedIn)
EXPERIENCE_LEVELS = {
    "Internship": "1",
    "Entry level": "2",
    "Associate": "3",
    "Mid-Senior level": "4",
    "Director": "5",
    "Executive": "6",
}

# Job type codes (LinkedIn)
JOB_TYPES = {
    "Full-time": "F",
    "Part-time": "P",
    "Contract": "C",
    "Temporary": "T",
    "Volunteer": "V",
    "Internship": "I",
    "Other": "O",
}

# Remote codes (LinkedIn)
REMOTE_TYPES = {
    "On-site": "1",
    "Remote": "2",
    "Hybrid": "3",
}

# Date posted codes (LinkedIn)
DATE_POSTED = {
    "Any Time": "",
    "Past Month": "r2592000",
    "Past Week": "r604800",
    "Past 24 hours": "r86400",
}

# Sort codes
SORT_BY = {
    "Recent": "DD",
    "Relevant": "R",
}

# Default bot config
DEFAULT_CONFIG = {
    "linkedin_email": "",
    "linkedin_password": "",
    "naukri_email": "",
    "naukri_password": "",
    "platforms": ["linkedin"],
    "keywords": [],
    "location": ["India"],
    "experience_levels": ["Entry level"],
    "job_types": ["Full-time"],
    "remote": ["Remote", "Hybrid", "On-site"],
    "date_posted": "Past Week",
    "sort_by": "Recent",
    "blacklist_companies": [],
    "blacklist_titles": [],
    "follow_companies": False,
    "headless": False,
    "dry_run": False,
    "max_applications": 50,
    "preferred_resume": "",
}

# AWS Bedrock Claude API
BEDROCK_API_KEY = os.environ.get("BEDROCK_API_KEY", "")
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-east-1")
BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"
BEDROCK_API_URL = f"https://bedrock-runtime.{BEDROCK_REGION}.amazonaws.com/model/{BEDROCK_MODEL_ID}/invoke"
