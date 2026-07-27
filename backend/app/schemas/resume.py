from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ParsedResumeSummary(BaseModel):
    skills: list[str] = []
    experience: list[dict] = []
    education: list[dict] = []


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    file_type: str
    is_default: bool
    created_at: datetime


class ResumeUploadResponse(ResumeResponse):
    parsed: ParsedResumeSummary
