"""Business logic for real user information, templates, and resumes."""

import re
import uuid
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile

from app.core.constants import MAX_RESUME_UPLOAD_SIZE_MB, SUPPORTED_RESUME_EXTENSIONS
from app.repositories import EZApplyRepository, decode_json


RESUME_DIRECTORY = Path(__file__).resolve().parents[3] / "data" / "resumes"


def _clean_strings(values: list[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = value.strip()
        normalized = cleaned.casefold()
        if cleaned and normalized not in seen:
            unique.append(cleaned)
            seen.add(normalized)
    return unique


def _initials(fields: list[dict[str, str]]) -> str:
    name = next(
        (field["value"] for field in fields if field["label"].casefold() == "full name"),
        "",
    )
    return "".join(part[:1].upper() for part in name.split()[:2])


def _parse_text_resume(path: Path) -> dict[str, Any]:
    """Extract only basic real fields from a text resume when possible."""
    if path.suffix.lower() != ".txt":
        return {}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}

    parsed: dict[str, Any] = {}
    email_match = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text)
    if email_match:
        parsed["email"] = email_match.group(0)
    phone_match = re.search(r"(?:\+?\d[\d .()-]{7,}\d)", text)
    if phone_match:
        parsed["phone"] = phone_match.group(0).strip()
    return parsed


class SavedInfoService:
    """Persists user-owned data without sample records or fallback values."""

    def __init__(self, repository: EZApplyRepository):
        self.repository = repository

    def profile(self) -> dict[str, Any]:
        profile = self.repository.get_profile()
        if profile is None:
            return {"fields": [], "skills": [], "initials": ""}
        fields = decode_json(profile.fields_json, [])
        skills = decode_json(profile.skills_json, [])
        return {
            "fields": fields if isinstance(fields, list) else [],
            "skills": skills if isinstance(skills, list) else [],
            "initials": _initials(fields if isinstance(fields, list) else []),
        }

    def update_profile(self, fields: list[dict[str, str]], skills: list[str]) -> dict[str, Any]:
        cleaned_fields = [
            {"label": field["label"].strip(), "value": field["value"].strip()}
            for field in fields
            if field["label"].strip()
        ]
        cleaned_skills = _clean_strings(skills)
        profile = self.repository.save_profile(cleaned_fields, cleaned_skills)
        return {
            "fields": decode_json(profile.fields_json, []),
            "skills": decode_json(profile.skills_json, []),
            "initials": _initials(cleaned_fields),
        }

    def keywords(self) -> dict[str, list[str]]:
        stored = self.repository.get_json_setting(
            "saved_keywords", {"saved_keywords": [], "excluded_keywords": []}
        )
        if not isinstance(stored, dict):
            stored = {}
        return {
            "saved_keywords": _clean_strings(stored.get("saved_keywords", [])),
            "excluded_keywords": _clean_strings(stored.get("excluded_keywords", [])),
        }

    def update_keywords(self, saved: list[str], excluded: list[str]) -> dict[str, list[str]]:
        data = {
            "saved_keywords": _clean_strings(saved),
            "excluded_keywords": _clean_strings(excluded),
        }
        self.repository.save_json_setting("saved_keywords", data)
        return data

    @staticmethod
    def _template_response(template: Any) -> dict[str, Any]:
        return {
            "id": template.id,
            "name": template.name,
            "content": template.content,
            "last_edited": template.updated_at,
        }

    def templates(self) -> list[dict[str, Any]]:
        return [self._template_response(template) for template in self.repository.list_templates()]

    def create_template(self, name: str, content: str) -> dict[str, Any]:
        return self._template_response(self.repository.add_template(name.strip(), content))

    def delete_template(self, template_id: int) -> bool:
        return self.repository.delete_template(template_id)

    @staticmethod
    def _resume_response(resume: Any) -> dict[str, Any]:
        return {
            "id": resume.id,
            "filename": resume.filename,
            "size_bytes": resume.size_bytes,
            "content_type": resume.content_type,
            "created_at": resume.created_at,
            "is_active": resume.is_active,
            "parsed_data": decode_json(resume.parsed_json, {}),
        }

    def resumes(self) -> list[dict[str, Any]]:
        return [self._resume_response(resume) for resume in self.repository.list_resumes()]

    def active_resume(self) -> Any | None:
        return self.repository.get_active_resume()

    async def upload_resume(self, upload: UploadFile) -> dict[str, Any]:
        filename = Path(upload.filename or "").name
        extension = Path(filename).suffix.lower()
        if not filename or extension not in SUPPORTED_RESUME_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Choose a supported resume file.")

        content = await upload.read()
        max_size = MAX_RESUME_UPLOAD_SIZE_MB * 1024 * 1024
        if not content:
            raise HTTPException(status_code=400, detail="Resume file is empty.")
        if len(content) > max_size:
            raise HTTPException(status_code=413, detail="Resume file is too large.")

        RESUME_DIRECTORY.mkdir(parents=True, exist_ok=True)
        storage_path = RESUME_DIRECTORY / f"{uuid.uuid4().hex}{extension}"
        storage_path.write_bytes(content)
        parsed_data = _parse_text_resume(storage_path)
        resume = self.repository.add_resume(
            filename=filename,
            storage_path=str(storage_path),
            content_type=upload.content_type,
            size_bytes=len(content),
            parsed_data=parsed_data,
        )
        return self._resume_response(resume)

    def delete_resume(self, resume_id: int) -> bool:
        resume = self.repository.get_resume(resume_id)
        if resume is None:
            return False
        path = Path(resume.storage_path)
        self.repository.delete_resume(resume)
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return True
