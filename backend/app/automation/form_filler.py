"""
Generic form-filling logic shared across all platform adapters. Platform
adapters are responsible for opening the application modal/page; FormFiller
takes it from there: read fields -> match against SavedInfo/Resume/learned
answers -> fill -> submit, pausing on anything unmapped.
"""
from typing import Literal

from playwright.async_api import Page
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.learning import LearningService
from app.services.saved_info import SavedInfoService

Outcome = Literal["submitted", "paused", "skipped"]


class FormFiller:
    def __init__(self, db: AsyncSession, bot_run_id: str):
        self.db = db
        self.bot_run_id = bot_run_id
        self.saved_info_service = SavedInfoService(db)
        self.learning_service = LearningService(db)

    async def fill_and_submit(self, page: Page, adapter, job: dict) -> Outcome:
        """
        1. adapter.open_application_modal(page, job)
        2. fields = adapter.read_form_fields(page)   # -> list[{label, type, selector}]
        3. For each field:
             - try direct match against SavedInfo (name/email/phone/etc.)
             - else try LearningService.find_known_answer(label)
             - else -> record_unknown_question(...) and return "paused"
        4. adapter.submit(page)
        5. return "submitted"

        This is left as a scaffold: the exact field-matching heuristics and
        DOM selectors are highly platform-specific and need to be built/
        tested against each platform's real application modal.
        """
        saved_info = await self.saved_info_service.get()

        fields = await adapter.read_form_fields(page)

        for field in fields:
            value = self._match_saved_info(field, saved_info)

            if value is None:
                value = await self.learning_service.find_known_answer(field["label"])

            if value is None:
                await self.learning_service.record_unknown_question(
                    bot_run_id=self.bot_run_id,
                    question_text=field["label"],
                    field_type=field["type"],
                    job_title=job.get("title"),
                    company=job.get("company"),
                )
                return "paused"

            await adapter.fill_field(page, field, value)

        await adapter.submit(page)
        return "submitted"

    @staticmethod
    def _match_saved_info(field: dict, saved_info) -> str | None:
        label = field["label"].strip().lower()
        direct_map = {
            "full name": saved_info.full_name,
            "name": saved_info.full_name,
            "email": saved_info.email,
            "phone": saved_info.phone,
            "location": saved_info.location,
            "linkedin": saved_info.linkedin_url,
            "portfolio": saved_info.portfolio_url,
            "expected salary": saved_info.salary_expectation,
            "work authorization": saved_info.work_authorization,
        }
        return direct_map.get(label)
