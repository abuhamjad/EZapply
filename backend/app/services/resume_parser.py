"""
Resume parsing: extracts raw text via pdfplumber/python-docx, then
(optionally) calls an LLM to structure it into skills/experience/education.

Keep this isolated from ResumeService so you can swap the extraction
strategy (regex heuristics vs. LLM call) without touching storage logic.
"""
import re
from pathlib import Path

import pdfplumber
from docx import Document

COMMON_SKILLS = [
    "python", "javascript", "typescript", "react", "node.js", "fastapi", "django",
    "flask", "sql", "postgresql", "mongodb", "aws", "docker", "kubernetes", "git",
    "java", "c++", "go", "rust", "sqlalchemy", "playwright", "selenium",
]


def extract_text(file_path: Path, file_type: str) -> str:
    if file_type == "pdf":
        text_parts: list[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    if file_type == "docx":
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    if file_type == "txt":
        return file_path.read_text(encoding="utf-8", errors="ignore")

    raise ValueError(f"Unsupported file type: {file_type}")


def extract_skills(raw_text: str) -> list[str]:
    text_lower = raw_text.lower()
    return [skill for skill in COMMON_SKILLS if skill in text_lower]


def extract_email(raw_text: str) -> str | None:
    match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", raw_text)
    return match.group(0) if match else None


def extract_phone(raw_text: str) -> str | None:
    match = re.search(r"(\+?\d[\d\-\s()]{8,}\d)", raw_text)
    return match.group(0).strip() if match else None


def parse_resume(file_path: Path, file_type: str) -> dict:
    """
    Returns a dict of {raw_text, skills, experience, education}.

    NOTE: `experience` / `education` extraction below is a placeholder
    heuristic. For production quality, swap this block for a call to the
    Claude API (see anthropic_api_in_artifacts pattern) with a prompt like:
    "Extract work experience and education as JSON from this resume text."
    """
    raw_text = extract_text(file_path, file_type)
    return {
        "raw_text": raw_text,
        "skills": extract_skills(raw_text),
        "experience": [],  # TODO: structure via LLM call or section-header regex
        "education": [],   # TODO: same as above
        "email": extract_email(raw_text),
        "phone": extract_phone(raw_text),
    }
