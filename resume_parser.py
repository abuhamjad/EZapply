# ============================================================
# Resume Parser — Extract text from PDF/DOCX resumes
# ============================================================

import os
import json
import requests
from typing import Dict, List, Optional

import constants


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text content from a PDF file."""
    try:
        import PyPDF2
        text = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"❌ PDF extraction error: {e}")
        return ""


def extract_text_from_docx(filepath: str) -> str:
    """Extract text content from a DOCX file."""
    try:
        import docx
        doc = docx.Document(filepath)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text.strip()
    except Exception as e:
        print(f"❌ DOCX extraction error: {e}")
        return ""


def extract_text(filepath: str) -> str:
    """Extract text from resume file based on extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(filepath)
    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    else:
        return ""


def _extract_contact_info(text: str) -> Dict:
    """Extract phone, email, name, LinkedIn URL via regex."""
    import re
    info = {"phone": "", "email": "", "name": "", "linkedin_url": ""}

    # Email
    emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
    if emails:
        info["email"] = emails[0]

    # Phone — multiple formats
    phones = re.findall(
        r'(?:\+?\d{1,3}[\s\-.]?)?\(?\d{2,4}\)?[\s\-.]?\d{3,5}[\s\-.]?\d{3,5}',
        text
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


def parse_resume_with_ai(resume_text: str, groq_api_key: str) -> Dict:
    """Use Groq AI to extract structured data from resume text."""
    # Always extract contact info via regex first
    contact = _extract_contact_info(resume_text)

    if not groq_api_key or not resume_text:
        result = _basic_parse(resume_text)
        # Merge regex contact info
        for k in ("phone", "email", "name", "linkedin_url"):
            if contact.get(k) and not result.get(k):
                result[k] = contact[k]
        return result

    prompt = f"""Analyze this resume and extract structured information. Return ONLY valid JSON with these exact keys:
{{
    "name": "candidate full name",
    "email": "email if found",
    "phone": "phone number with country code if found",
    "linkedin_url": "linkedin profile URL if found",
    "skills": ["list", "of", "technical", "skills"],
    "experience_years": 0,
    "job_titles": ["relevant job titles to search for"],
    "search_keywords": ["top 5-8 keywords for job search"],
    "education": "highest education level and degree",
    "current_location": "city, country if found",
    "summary": "2-3 sentence professional summary"
}}

Resume:
{resume_text[:3000]}"""

    try:
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": constants.GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 1024,
        }
        resp = requests.post(constants.GROQ_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

        # Extract JSON from response
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            parsed = json.loads(content[start:end])
            # Merge regex contact info as fallback
            for k in ("phone", "email", "name", "linkedin_url"):
                if contact.get(k) and not parsed.get(k):
                    parsed[k] = contact[k]
            return parsed
        result = _basic_parse(resume_text)
        for k in ("phone", "email", "name", "linkedin_url"):
            if contact.get(k) and not result.get(k):
                result[k] = contact[k]
        return result
    except Exception as e:
        print(f"⚠️ AI parsing fallback: {e}")
        result = _basic_parse(resume_text)
        for k in ("phone", "email", "name", "linkedin_url"):
            if contact.get(k) and not result.get(k):
                result[k] = contact[k]
        return result


def _basic_parse(text: str) -> Dict:
    """Basic keyword extraction without AI."""
    common_skills = [
        "python", "javascript", "java", "react", "node", "sql", "html", "css",
        "typescript", "angular", "vue", "django", "flask", "aws", "docker",
        "kubernetes", "git", "mongodb", "postgresql", "machine learning",
        "data science", "tensorflow", "pytorch", "c++", "c#", ".net",
        "spring", "ruby", "go", "rust", "swift", "kotlin", "php", "laravel",
    ]
    text_lower = text.lower()
    found_skills = [s for s in common_skills if s in text_lower]

    return {
        "name": "",
        "email": "",
        "phone": "",
        "linkedin_url": "",
        "skills": found_skills[:10],
        "experience_years": 0,
        "job_titles": found_skills[:3],
        "search_keywords": found_skills[:6],
        "education": "",
        "current_location": "",
        "summary": "Resume parsed without AI. Add Groq API key for better results.",
    }


def list_resumes(resumes_dir: str = "resumes") -> List[Dict]:
    """List all resume files in the resumes directory."""
    if not os.path.exists(resumes_dir):
        os.makedirs(resumes_dir, exist_ok=True)
        return []

    resumes = []
    supported = (".pdf", ".docx", ".doc", ".txt")
    for fname in os.listdir(resumes_dir):
        ext = os.path.splitext(fname)[1].lower()
        if ext in supported:
            fpath = os.path.join(resumes_dir, fname)
            resumes.append({
                "name": fname,
                "path": fpath,
                "size": os.path.getsize(fpath),
                "type": ext[1:].upper(),
            })
    return resumes
