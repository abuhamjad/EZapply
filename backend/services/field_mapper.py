# ============================================================
# Field Mapper — Map form labels to resume values
# ============================================================
from typing import Dict, Optional


def build_field_map(resume_data: Dict) -> Dict[str, str]:
    """Build mapping: field keyword → value from parsed resume."""
    phone = resume_data.get("phone", "")
    email = resume_data.get("email", "")
    name = resume_data.get("name", "")
    city = resume_data.get("current_location", "")
    linkedin_url = resume_data.get("linkedin_url", "")
    first_name = name.split()[0] if name else ""
    last_name = " ".join(name.split()[1:]) if name and len(name.split()) > 1 else ""
    experience = str(resume_data.get("experience_years", 0))
    education = resume_data.get("education", "")
    summary = resume_data.get("summary", "")
    skills_str = ", ".join(resume_data.get("skills", [])[:10])
    profession = resume_data.get("profession", "")
    current_title = ""
    if resume_data.get("job_titles"):
        current_title = resume_data["job_titles"][0]

    return {
        "phone": phone, "mobile": phone, "cell": phone,
        "email": email, "e-mail": email,
        "first name": first_name, "given name": first_name,
        "last name": last_name, "surname": last_name, "family name": last_name,
        "full name": name, "city": city, "location": city,
        "current location": city, "linkedin": linkedin_url,
        "years of experience": experience, "experience": experience,
        "total experience": experience, "work experience": experience,
        "education": education, "degree": education, "qualification": education,
        "highest degree": education, "highest education": education,
        "headline": profession or current_title,
        "current title": current_title, "job title": current_title,
        "current role": current_title, "current position": current_title,
        "summary": summary, "cover letter": summary, "about": summary,
        "skills": skills_str,
        "github": resume_data.get("github_url", ""),
        "portfolio": resume_data.get("portfolio_url", ""),
        "website": resume_data.get("portfolio_url", ""),
    }
