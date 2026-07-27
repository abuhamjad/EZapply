from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class KeywordItem(BaseModel):
    id: int
    text: str
    kind: str = "include"
    count: int = 0


class KeywordCreate(BaseModel):
    text: str
    kind: str = "include"


class TemplateItem(BaseModel):
    id: int
    name: str
    last_edited: str


class TemplateCreate(BaseModel):
    name: str


class SavedInfoBase(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None

    target_titles: list[str] = []
    target_locations: list[str] = []
    salary_expectation: str | None = None
    work_authorization: str | None = None
    remote_preference: str | None = None

    custom_answers: dict[str, str] = {}

    saved_keywords: list[KeywordItem] = []
    excluded_keywords: list[KeywordItem] = []
    cover_letter_templates: list[TemplateItem] = []


class SavedInfoUpdate(SavedInfoBase):
    """Payload for PUT /api/saved-info. All fields optional."""

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        digits = "".join(ch for ch in v if ch.isdigit() or ch == "+")
        return digits or None


class SavedInfoResponse(SavedInfoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = 1
    updated_at: datetime | None = None
