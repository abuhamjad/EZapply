# ============================================================
# LinkedIn Search — URL generation for job search
# ============================================================
from typing import Dict, List
from backend.config import (
    LINKEDIN_JOBS_SEARCH, GEO_IDS, JOB_TYPES, REMOTE_TYPES,
    EXPERIENCE_LEVELS, DATE_POSTED, SORT_BY,
)


def generate_search_urls(config: Dict, resume_data: Dict = None) -> List[str]:
    """Generate LinkedIn Easy Apply search URLs from config."""
    urls = []
    kws = config.get("keywords") or (resume_data or {}).get("search_keywords", ["software engineer"])
    locs = config.get("location", ["India"])

    for loc in locs:
        for kw in kws:
            u = f"{LINKEDIN_JOBS_SEARCH}?f_AL=true&keywords={kw}"

            jtc = [JOB_TYPES[j] for j in config.get("job_types", []) if j in JOB_TYPES]
            if jtc:
                u += "&f_JT=" + "%2C".join(jtc)

            rtc = [REMOTE_TYPES[r] for r in config.get("remote", []) if r in REMOTE_TYPES]
            if rtc:
                u += "&f_WT=" + "%2C".join(rtc)

            u += f"&location={loc}"
            gid = GEO_IDS.get(loc.lower(), "")
            if gid:
                u += f"&geoId={gid}"

            exc = [EXPERIENCE_LEVELS[e] for e in config.get("experience_levels", []) if e in EXPERIENCE_LEVELS]
            if exc:
                u += "&f_E=" + "%2C".join(exc)

            dp = DATE_POSTED.get(config.get("date_posted", "Past Week"), "")
            if dp:
                u += f"&f_TPR={dp}"

            sc = SORT_BY.get(config.get("sort_by", "Recent"), "DD")
            u += f"&sortBy={sc}"
            urls.append(u)
    return urls
