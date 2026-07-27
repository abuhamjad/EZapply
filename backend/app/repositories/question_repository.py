from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import QuestionKnowledge, ScreeningQuestion


class QuestionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Screening questions (per-run, pending user input) ---
    async def create_screening_question(self, question: ScreeningQuestion) -> ScreeningQuestion:
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        return question

    async def get_screening_question(self, question_id: str) -> ScreeningQuestion | None:
        result = await self.db.execute(select(ScreeningQuestion).where(ScreeningQuestion.id == question_id))
        return result.scalar_one_or_none()

    async def get_latest_unresolved(self, bot_run_id: str) -> ScreeningQuestion | None:
        result = await self.db.execute(
            select(ScreeningQuestion)
            .where(ScreeningQuestion.bot_run_id == bot_run_id, ScreeningQuestion.resolved.is_(False))
            .order_by(ScreeningQuestion.created_at.desc())
        )
        return result.scalars().first()

    async def resolve_screening_question(self, question: ScreeningQuestion, answer: str) -> ScreeningQuestion:
        question.answer = answer
        question.resolved = True
        await self.db.commit()
        await self.db.refresh(question)
        return question

    # --- Learned answer bank (cross-run reuse) ---
    async def find_known_answer(self, question_text: str) -> QuestionKnowledge | None:
        result = await self.db.execute(
            select(QuestionKnowledge).where(QuestionKnowledge.question_text == question_text)
        )
        return result.scalar_one_or_none()

    async def upsert_knowledge(self, question_text: str, answer: str) -> QuestionKnowledge:
        existing = await self.find_known_answer(question_text)
        if existing:
            existing.answer = answer
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        row = QuestionKnowledge(question_text=question_text, answer=answer)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row
