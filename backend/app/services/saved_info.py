import json
import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bot import BotConfig
from app.models.saved_info import SavedInfo
from app.repositories.saved_info_repository import SavedInfoRepository
from app.schemas.saved_info import (
    KeywordItem,
    SavedInfoResponse,
    SavedInfoUpdate,
    TemplateItem,
)


def parse_annual_salary(val: str | int | None) -> int:
    """Parse salary input into an annual integer in INR."""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        if 0 < val <= 100:
            return int(val * 100000)
        return int(val)

    text = str(val).strip().lower()
    if not text:
        return 0

    # Check for LPA / Lakhs format: e.g. "6.5 LPA", "12 Lakh"
    lpa_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lac)", text)
    if lpa_match:
        return int(float(lpa_match.group(1)) * 100000)

    # Extract all digits
    digits = re.sub(r"[^\d.]", "", text)
    if not digits:
        return 0
    try:
        num = float(digits)
        if 0 < num <= 100:
            return int(num * 100000)
        return int(num)
    except ValueError:
        return 0


class SavedInfoService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SavedInfoRepository(db)

    async def get(self) -> SavedInfoResponse:
        row = await self.repo.get_or_create()

        saved_kws_json = json.loads(row.saved_keywords_json) if row.saved_keywords_json else []
        tmpl_json = json.loads(row.cover_letter_templates_json) if row.cover_letter_templates_json else []

        saved_kws = [KeywordItem(**k) for k in saved_kws_json if k["kind"] == "include"]
        excl_kws = [KeywordItem(**k) for k in saved_kws_json if k["kind"] == "exclude"]
        tmpl_items = [TemplateItem(**t) for t in tmpl_json]

        return SavedInfoResponse(
            id=row.id,
            full_name=row.full_name or "",
            email=row.email or "",
            phone=row.phone or "",
            location=row.location or "",
            linkedin_url=row.linkedin_url or "",
            portfolio_url=row.portfolio_url or "",
            target_titles=(row.target_titles or "").split(",") if row.target_titles else [],
            target_locations=(row.target_locations or "").split(",") if row.target_locations else [],
            salary_expectation=row.salary_expectation or "",
            work_authorization=row.work_authorization or "",
            remote_preference=row.remote_preference or "",
            custom_answers=json.loads(row.custom_answers_json) if row.custom_answers_json else {},
            saved_keywords=saved_kws,
            excluded_keywords=excl_kws,
            cover_letter_templates=tmpl_items,
            updated_at=row.updated_at,
        )

    async def update(self, payload: SavedInfoUpdate) -> SavedInfoResponse:
        row = await self.repo.get_or_create()
        fields = {
            "full_name": payload.full_name,
            "email": payload.email,
            "phone": payload.phone,
            "location": payload.location,
            "linkedin_url": payload.linkedin_url,
            "portfolio_url": payload.portfolio_url,
            "target_titles": ",".join(payload.target_titles) if payload.target_titles else None,
            "target_locations": ",".join(payload.target_locations) if payload.target_locations else None,
            "salary_expectation": payload.salary_expectation,
            "work_authorization": payload.work_authorization,
            "remote_preference": payload.remote_preference,
            "custom_answers_json": json.dumps(payload.custom_answers) if payload.custom_answers else None,
        }
        fields = {k: v for k, v in fields.items() if v is not None}
        await self.repo.update(row, **fields)

        # Synchronize salary expectation with BotConfig.min_salary (annual INR)
        if payload.salary_expectation is not None:
            sal_int = parse_annual_salary(payload.salary_expectation)
            if sal_int > 0:
                cfg_res = await self.db.execute(select(BotConfig).where(BotConfig.id == "default"))
                cfg = cfg_res.scalar_one_or_none()
                if cfg:
                    cfg.min_salary = sal_int
                    await self.db.commit()

        return await self.get()

    async def _get_keywords_list(self) -> list[dict]:
        row = await self.repo.get_or_create()
        return json.loads(row.saved_keywords_json) if row.saved_keywords_json else []

    async def _save_keywords_list(self, keywords: list[dict]):
        row = await self.repo.get_or_create()
        await self.repo.update(row, saved_keywords_json=json.dumps(keywords))

    async def add_keyword(self, text: str, kind: str) -> KeywordItem:
        keywords = await self._get_keywords_list()
        new_id = max([k.get("id", 0) for k in keywords], default=0) + 1
        item = {"id": new_id, "text": text, "kind": kind, "count": 1}
        keywords.append(item)
        await self._save_keywords_list(keywords)
        return KeywordItem(**item)

    async def delete_keyword(self, keyword_id: int) -> None:
        keywords = await self._get_keywords_list()
        keywords = [k for k in keywords if k.get("id") != keyword_id]
        await self._save_keywords_list(keywords)

    async def _get_templates_list(self) -> list[dict]:
        row = await self.repo.get_or_create()
        return json.loads(row.cover_letter_templates_json) if row.cover_letter_templates_json else []

    async def _save_templates_list(self, templates: list[dict]):
        row = await self.repo.get_or_create()
        await self.repo.update(row, cover_letter_templates_json=json.dumps(templates))

    async def add_template(self, name: str) -> TemplateItem:
        from datetime import datetime, timezone
        templates = await self._get_templates_list()
        new_id = max([t.get("id", 0) for t in templates], default=0) + 1
        item = {"id": new_id, "name": name, "last_edited": datetime.now(timezone.utc).isoformat()}
        templates.append(item)
        await self._save_templates_list(templates)
        return TemplateItem(**item)

    async def delete_template(self, template_id: int) -> None:
        templates = await self._get_templates_list()
        templates = [t for t in templates if t.get("id") != template_id]
        await self._save_templates_list(templates)

    async def is_profile_complete(self) -> bool:
        row = await self.repo.get_or_create()
        return bool(row.full_name and row.email and row.phone and row.target_titles)
