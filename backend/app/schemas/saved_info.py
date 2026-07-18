from datetime import datetime

from pydantic import BaseModel, Field


class ProfileField(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    value: str = Field(max_length=500)


class ProfileResponse(BaseModel):
    fields: list[ProfileField] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    initials: str = ""


class ProfileUpdateRequest(BaseModel):
    fields: list[ProfileField] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class KeywordsResponse(BaseModel):
    saved_keywords: list[str] = Field(default_factory=list)
    excluded_keywords: list[str] = Field(default_factory=list)


class KeywordsUpdateRequest(BaseModel):
    saved_keywords: list[str] = Field(default_factory=list)
    excluded_keywords: list[str] = Field(default_factory=list)


class CoverLetterTemplate(BaseModel):
    id: int
    name: str
    content: str = ""
    last_edited: datetime


class TemplatesResponse(BaseModel):
    templates: list[CoverLetterTemplate] = Field(default_factory=list)


class CreateTemplateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    content: str = Field(default="", max_length=20000)


class ResumeResponse(BaseModel):
    id: int
    filename: str
    size_bytes: int
    content_type: str | None = None
    created_at: datetime
    is_active: bool
    parsed_data: dict = Field(default_factory=dict)


class ResumesResponse(BaseModel):
    resumes: list[ResumeResponse] = Field(default_factory=list)
