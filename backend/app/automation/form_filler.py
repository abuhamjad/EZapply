"""
Generic form-filling logic shared across all platform adapters. Platform
adapters are responsible for opening the application modal/page; FormFiller
takes it from there: read fields -> match against SavedInfo/Resume/learned
answers -> fill -> submit, pausing on anything unmapped.
"""
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
        # Normalize: remove punctuation, collapse whitespace
        import string as _string
        label = label.translate(str.maketrans('', '', _string.punctuation)).strip()
        label = " ".join(label.split())

        # Name variants
        if "first name" in label:
            parts = (saved_info.full_name or "").split()
            return parts[0] if parts else None
        if "last name" in label or "surname" in label or "family name" in label:
            parts = (saved_info.full_name or "").split()
            return parts[-1] if len(parts) > 1 else (parts[0] if parts else None)
        if "full name" in label or (
            "name" in label
            and "first" not in label
            and "last" not in label
            and "company" not in label
            and "school" not in label
            and "university" not in label
        ):
            return saved_info.full_name

        # Contact
        if "email" in label:
            return saved_info.email

        # Phone — strip to digits only for "mobile phone number" fields
        if "phone" in label or "mobile" in label:
            phone = saved_info.phone or ""
            if field.get("type") == "text":
                # LinkedIn mobile number field expects digits only (no country code)
                digits_only = "".join(c for c in phone if c.isdigit())
                # Remove leading 91 if it's a 12-digit Indian number
                if len(digits_only) == 12 and digits_only.startswith("91"):
                    digits_only = digits_only[2:]
                return digits_only if digits_only else phone
            return phone

        # Location
        if any(kw in label for kw in ["location", "city", "address", "pincode", "zip", "state"]):
            return saved_info.location

        # Professional links
        if "linkedin" in label and "url" in label:
            return saved_info.linkedin_url
        if "linkedin" in label:
            return saved_info.linkedin_url
        if "portfolio" in label or "website" in label or "github" in label:
            return saved_info.portfolio_url

        # Compensation
        if "salary" in label or "compensation" in label or "ctc" in label or "package" in label:
            return saved_info.salary_expectation

        # Work authorization / visa
        if any(kw in label for kw in ["work authorization", "sponsorship", "visa", "authorized", "eligible"]):
            return saved_info.work_authorization

        # Years of experience — derive from profile if possible, default safe answer
        if "years of experience" in label or "years experience" in label:
            return "1"  # conservative default; LearningService can override

        # Cover letter / summary fields
        if "cover letter" in label or "summary" in label or "about yourself" in label or "tell us about" in label:
            name = (saved_info.full_name or "Candidate").split()[0]
            titles = saved_info.target_titles or []
            title_str = titles[0] if titles else "Software Developer"
            return (
                f"Hi, I am {name}, a passionate {title_str} looking for exciting opportunities. "
                f"I am eager to contribute my skills and grow with your team."
            )

        return None

