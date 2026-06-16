# ============================================================
# Resume Parser — Extract text from PDF/DOCX resumes
# ============================================================

import os
import json
import re
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


def _call_bedrock(prompt: str, max_tokens: int = 2048) -> str:
    """Call AWS Bedrock Claude API."""
    api_key = constants.BEDROCK_API_KEY
    if not api_key:
        return ""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        }
        resp = requests.post(
            constants.BEDROCK_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        return result["content"][0]["text"]
    except Exception as e:
        print(f"⚠️ Bedrock API error: {e}")
        return ""


def parse_resume_with_ai(resume_text: str, api_key: str = "") -> Dict:
    """Use AWS Bedrock Claude to extract structured data from resume text."""
    # Always extract contact info via regex first
    contact = _extract_contact_info(resume_text)

    if not resume_text or not constants.BEDROCK_API_KEY:
        result = _basic_parse(resume_text)
        for k in ("phone", "email", "name", "linkedin_url"):
            if contact.get(k) and not result.get(k):
                result[k] = contact[k]
        return result

    prompt = f"""You are a resume parser. Analyze this resume and extract ONLY what is ACTUALLY written in it.
DO NOT invent or assume skills/titles not mentioned. Return ONLY valid JSON.

{{
    "name": "candidate full name",
    "email": "email if found",
    "phone": "phone number with country code if found",
    "linkedin_url": "linkedin profile URL if found",
    "skills": ["ONLY skills explicitly mentioned in the resume - programming languages, frameworks, tools, etc. that the candidate actually lists or demonstrates"],
    "experience_years": 0,
    "job_titles": ["realistic job titles this candidate should apply for based on their education, skills, and experience level - e.g. 'AI/ML Intern', 'Python Developer Fresher', 'Junior Software Engineer'"],
    "search_keywords": ["job search keywords matching candidate's actual domain and skill level"],
    "education": "highest education level, degree name, and institution",
    "current_location": "city, country if found",
    "summary": "2-3 sentence professional summary based on actual resume content",
    "profession": "candidate's primary profession/domain (e.g. 'AI/ML Engineering', 'Web Development', 'Data Science')",
    "experience_level": "Fresher/Intern/Junior/Mid/Senior based on actual experience"
}}

RULES:
- Only include skills the candidate ACTUALLY mentions (by name or demonstrated in projects)
- Do NOT include skills like 'React', 'Django', 'Docker' if they are NOT in the resume
- job_titles must match candidate's REAL experience level (student = Intern/Fresher/Junior)
- search_keywords should be for jobs the candidate is QUALIFIED for

Resume:
{resume_text[:6000]}"""

    try:
        content = _call_bedrock(prompt, 2048)
        if content:
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
    except Exception as e:
        print(f"⚠️ AI parsing fallback: {e}")

    result = _basic_parse(resume_text)
    for k in ("phone", "email", "name", "linkedin_url"):
        if contact.get(k) and not result.get(k):
            result[k] = contact[k]
    return result


def _basic_parse(text: str) -> Dict:
    """Keyword extraction from resume without AI. Uses word-boundary matching to avoid false positives."""
    # Skills that need exact word-boundary matching to avoid false positives
    # e.g. "java" should NOT match "javascript", "go" should NOT match "going"
    common_skills = [
        # Languages (all need word boundary)
        "python", "javascript", "java", "c\\+\\+", "c#", "golang",
        "rust", "swift", "kotlin", "php", "ruby", "typescript", "scala",
        "perl", "matlab", "dart", "lua", "haskell", "elixir", "solidity",
        # Frontend
        "react", "reactjs", "react\\.js", "angular", "angularjs", "vue",
        "vue\\.js", "vuejs", "svelte", "next\\.js", "nextjs", "nuxt",
        "gatsby", "html", "html5", "css", "css3", "sass", "scss",
        "tailwind", "tailwindcss", "bootstrap", "material ui",
        "jquery", "webpack", "vite", "redux",
        # Backend
        "node\\.js", "nodejs", "express", "express\\.js",
        "django", "flask", "fastapi", "spring boot", "spring",
        "\\.net", "asp\\.net", "laravel", "rails", "ruby on rails",
        "nestjs", "nest\\.js",
        # Databases
        "sql", "mysql", "postgresql", "postgres", "mongodb", "redis",
        "elasticsearch", "firebase", "sqlite", "oracle", "graphql",
        # Cloud & DevOps
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "ansible", "jenkins", "ci/cd", "nginx", "linux",
        # AI/ML/Data
        "machine learning", "deep learning", "data science",
        "artificial intelligence", "natural language processing",
        "nlp", "computer vision", "tensorflow", "pytorch",
        "keras", "scikit-learn", "pandas", "numpy", "opencv",
        "llm", "langchain", "data analysis", "power bi", "tableau",
        # Mobile
        "android", "ios", "react native", "flutter",
        # Tools
        "git", "github", "gitlab", "jira", "figma", "postman",
        # Testing
        "selenium", "jest", "cypress", "pytest",
        # Concepts
        "agile", "scrum", "devops", "microservices", "rest", "api",
    ]

    text_lower = text.lower()
    found_skills = []
    seen = set()

    for skill_pattern in common_skills:
        # Build word-boundary regex for every skill
        # This prevents "java" matching inside "javascript", "go" inside "going", etc.
        pattern = r'(?<![a-zA-Z])' + skill_pattern + r'(?![a-zA-Z])'
        try:
            if re.search(pattern, text_lower):
                # Clean display name (remove regex escapes)
                display_name = skill_pattern.replace("\\+\\+", "++").replace("\\.", ".").replace("\\", "")
                if display_name not in seen:
                    found_skills.append(display_name)
                    seen.add(display_name)
        except: continue

    # Generate proper job titles from skills (not raw skill names)
    job_titles = []
    if any(s in seen for s in ("machine learning", "artificial intelligence", "deep learning", "nlp", "llm")):
        job_titles.extend(["AI/ML Intern", "Machine Learning Engineer", "AI Developer"])
    if any(s in seen for s in ("python", "java", "javascript", "c++", "c#")):
        job_titles.extend(["Software Developer", "Junior Software Engineer"])
    if any(s in seen for s in ("react", "angular", "vue", "html", "css", "javascript")):
        job_titles.extend(["Frontend Developer", "Web Developer"])
    if any(s in seen for s in ("node.js", "express", "django", "flask", "spring")):
        job_titles.extend(["Backend Developer", "Full Stack Developer"])
    if any(s in seen for s in ("data science", "data analysis", "pandas", "numpy", "tableau", "power bi")):
        job_titles.extend(["Data Analyst", "Data Science Intern"])
    if any(s in seen for s in ("android", "ios", "flutter", "react native")):
        job_titles.extend(["Mobile Developer", "App Developer"])
    if not job_titles:
        job_titles = ["Software Engineer Intern", "Junior Developer"]

    # Deduplicate
    job_titles = list(dict.fromkeys(job_titles))

    # Generate search keywords from skills + role names
    search_keywords = job_titles[:4] + found_skills[:6]
    search_keywords = list(dict.fromkeys(search_keywords))

    return {
        "name": "",
        "email": "",
        "phone": "",
        "linkedin_url": "",
        "skills": found_skills,
        "experience_years": 0,
        "job_titles": job_titles[:5],
        "search_keywords": search_keywords[:10],
        "education": "",
        "current_location": "",
        "summary": "Resume parsed without AI. Bedrock API will provide better results.",
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
