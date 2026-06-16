# ============================================================
# AI Resume Parser — Structured extraction via Claude
# ============================================================
import re
import json
from typing import Dict
from backend.services.ai.claude_service import claude_service
from backend.core.logger import get_logger

log = get_logger("ai_parser")


def extract_contact_info(text: str) -> Dict:
    """Extract phone, email, name, LinkedIn URL via regex."""
    info = {"phone": "", "email": "", "name": "", "linkedin_url": ""}

    # Email
    emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
    if emails:
        info["email"] = emails[0]

    # Phone
    phones = re.findall(
        r'(?:\+?\d{1,3}[\s\-.]?)?\(?\d{2,4}\)?[\s\-.]?\d{3,5}[\s\-.]?\d{3,5}', text
    )
    for p in phones:
        digits = re.sub(r'\D', '', p)
        if 10 <= len(digits) <= 15:
            info["phone"] = p.strip()
            break

    # LinkedIn URL
    linkedin = re.findall(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_/]+', text)
    if linkedin:
        info["linkedin_url"] = linkedin[0]

    # Name — first non-empty line that looks like a name
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in lines[:5]:
        clean = re.sub(r'[^a-zA-Z\s]', '', line).strip()
        words = clean.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            info["name"] = clean
            break

    return info


def parse_resume_with_ai(resume_text: str) -> Dict:
    """Use Claude to extract structured data from resume text."""
    contact = extract_contact_info(resume_text)

    if not resume_text or not claude_service.is_configured:
        from backend.services.resume.skill_parser import basic_parse
        result = basic_parse(resume_text)
        _merge_contact(result, contact)
        return result

    prompt = f"""You are a resume parser. Analyze this resume and extract ONLY what is ACTUALLY written.
DO NOT invent skills/titles not mentioned. Return ONLY valid JSON.

{{
    "name": "full name",
    "email": "email",
    "phone": "phone with country code",
    "linkedin_url": "linkedin URL",
    "skills": ["ONLY skills explicitly mentioned"],
    "experience_years": 0,
    "job_titles": ["realistic job titles matching experience level"],
    "search_keywords": ["job search keywords"],
    "education": "highest education",
    "current_location": "city, country",
    "summary": "2-3 sentence professional summary",
    "profession": "primary domain",
    "experience_level": "Fresher/Intern/Junior/Mid/Senior"
}}

RULES:
- Only include skills the candidate ACTUALLY mentions
- job_titles must match REAL experience level
- search_keywords should be for jobs candidate is QUALIFIED for

Resume:
{resume_text[:6000]}"""

    try:
        parsed = claude_service.call_json(prompt, max_tokens=2048, temperature=0.1)
        if parsed and isinstance(parsed, dict):
            _merge_contact(parsed, contact)
            return parsed
    except Exception as e:
        log.warning(f"AI parsing fallback: {e}")

    from backend.services.resume.skill_parser import basic_parse
    result = basic_parse(resume_text)
    _merge_contact(result, contact)
    return result


def _merge_contact(result: Dict, contact: Dict):
    """Merge regex-extracted contact info as fallback."""
    for k in ("phone", "email", "name", "linkedin_url"):
        if contact.get(k) and not result.get(k):
            result[k] = contact[k]
