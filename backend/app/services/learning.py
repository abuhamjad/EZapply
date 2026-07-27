from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import ScreeningQuestion
from app.repositories.question_repository import QuestionRepository


class LearningService:
    """
    Flow 4: when the automation engine hits an unknown field, it asks this
    service first (in case a similar question was already answered before),
    and if the user resolves a new one, this service records it for reuse.
    """

    def __init__(self, db: AsyncSession):
        self.repo = QuestionRepository(db)

    async def find_known_answer(self, question_text: str) -> str | None:
        row = await self.repo.find_known_answer(question_text.strip().lower())
        return row.answer if row else None

    async def record_unknown_question(
        self, bot_run_id: str, question_text: str, field_type: str, job_title: str | None, company: str | None
    ) -> ScreeningQuestion:
        question = ScreeningQuestion(
            bot_run_id=bot_run_id,
            question_text=question_text,
            field_type=field_type,
            job_title=job_title,
            company=company,
        )
        return await self.repo.create_screening_question(question)

    async def resolve_question(self, question_id: str, answer: str, remember: bool = True) -> ScreeningQuestion:
        question = await self.repo.get_screening_question(question_id)
        if question is None:
            raise ValueError(f"Screening question {question_id} not found")

        resolved = await self.repo.resolve_screening_question(question, answer)

        if remember:
            await self.repo.upsert_knowledge(resolved.question_text.strip().lower(), answer)

        return resolved
