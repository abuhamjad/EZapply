"""
Generic form-filling logic shared across all platform adapters. Platform
adapters are responsible for opening the application modal/page; FormFiller
takes it from there: read fields -> match against SavedInfo/Resume/learned
answers -> fill -> submit, pausing on anything unmapped.
"""
import string
from typing import Literal

from playwright.async_api import Page
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.question_repository import QuestionRepository
from app.services.learning import LearningService
from app.services.saved_info import SavedInfoService

Outcome = Literal["submitted", "paused", "skipped"]


class FormFiller:
    def __init__(self, db: AsyncSession, bot_run_id: str, resume_path: str | None = None):
        self.db = db
        self.bot_run_id = bot_run_id
        self.resume_path = resume_path
        self.saved_info_service = SavedInfoService(db)
        self.learning_service = LearningService(db)

    async def fill_and_submit(self, page: Page, adapter, job: dict) -> Outcome:
        """
        1. fields = adapter.read_form_fields(page)   # -> list[{label, type, selector}]
        2. For each field:
             - try direct match against SavedInfo (name/email/phone/etc.)
             - else try run-specific resolved answers
             - else try LearningService.find_known_answer(label)
             - else -> record_unknown_question(...) and return "paused"
        3. adapter.submit(page)
        4. return "submitted"
        """
        saved_info = await self.saved_info_service.get()

        fields = await adapter.read_form_fields(page)

        for field in fields:
            value = self._match_saved_info(field, saved_info)

            # Handle resume upload explicitly
            if field["type"] == "file" and "resume" in field["label"].lower():
                if self.resume_path:
                    value = self.resume_path
                else:
                    return "skipped"

            # Check for a run-specific resolved answer first
            if value is None:
                q_repo = QuestionRepository(self.db)
                resolved_questions = await q_repo.get_resolved_for_run(self.bot_run_id)
                for rq in resolved_questions:
                    if rq.question_text.strip().lower() == field["label"].strip().lower() and rq.answer:
                        value = rq.answer
                        break

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
        label = field["label"].lower()
        # Remove punctuation, strip whitespace, normalize spaces
        label = label.translate(str.maketrans('', '', string.punctuation)).strip()
        label = " ".join(label.split())

        # Substring/keyword containment matching for field labels
        if "first name" in label:
            return saved_info.full_name.split()[0] if saved_info.full_name else None
        if "last name" in label:
            return saved_info.full_name.split()[-1] if saved_info.full_name else None
        if "name" in label:
            return saved_info.full_name
        if "email" in label:
            return saved_info.email
        if "phone" in label or "mobile" in label:
            return saved_info.phone
        if "location" in label or "city" in label:
            return saved_info.location
        if "linkedin" in label:
            return saved_info.linkedin_url
        if "portfolio" in label or "website" in label:
            return saved_info.portfolio_url
        if "salary" in label:
            return saved_info.salary_expectation
        if "work authorization" in label or "sponsorship" in label:
            return saved_info.work_authorization

        return None
