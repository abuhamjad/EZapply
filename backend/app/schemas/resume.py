from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ParsedResumeSummary(BaseModel):
    skills: list[str] = []
    experience: list[dict] = []
    education: list[dict] = []


class ResumeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    file_type: str
    is_default: bool
    created_at: datetime


class ResumeResponse(ResumeBase):
    """Returned by GET /resumes — includes parsed summary."""
    parsed: ParsedResumeSummary = ParsedResumeSummary()


class ResumeUploadResponse(ResumeBase):
    """Returned after a successful upload."""
    parsed: ParsedResumeSummary
