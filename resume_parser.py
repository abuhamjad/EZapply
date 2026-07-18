"""Local resume extraction helpers used by the legacy compatibility server."""

import re
from pathlib import Path
from typing import Any


def extract_text(filepath: str) -> str:
    path = Path(filepath)
    try:
        if path.suffix.lower() == ".txt":
            return path.read_text(encoding="utf-8", errors="ignore").strip()
        if path.suffix.lower() == ".pdf":
            import PyPDF2

            with path.open("rb") as source:
                return "\n".join(
                    page.extract_text() or "" for page in PyPDF2.PdfReader(source).pages
                ).strip()
        if path.suffix.lower() in {".doc", ".docx"}:
            import docx

            document = docx.Document(path)
            return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
    except (OSError, ImportError, ValueError):
        return ""
    return ""


def parse_resume_with_ai(resume_text: str, api_key: str = "") -> dict[str, Any]:
    """Return only values actually found locally; no invented user profile."""
    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    email_match = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", resume_text)
    phone_match = re.search(r"(?:\+?\d[\d .()-]{7,}\d)", resume_text)
    return {
        "name": lines[0] if lines else "",
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0).strip() if phone_match else "",
        "linkedin_url": "",
        "skills": [],
        "experience_years": 0,
        "job_titles": [],
        "search_keywords": [],
        "education": "",
        "current_location": "",
        "summary": "",
    }


def list_resumes(resumes_dir: str = "resumes") -> list[dict[str, Any]]:
    directory = Path(resumes_dir)
    directory.mkdir(parents=True, exist_ok=True)
    supported = {".pdf", ".doc", ".docx", ".txt"}
    return [
        {
            "name": path.name,
            "path": str(path),
            "size": path.stat().st_size,
            "type": path.suffix.removeprefix(".").upper(),
        }
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in supported
    ]
