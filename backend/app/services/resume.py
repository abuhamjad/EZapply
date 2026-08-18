import json
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.schemas.resume import ParsedResumeSummary, ResumeUploadResponse
from app.services.resume_parser import parse_resume


class ResumeService:
    def __init__(self, db: AsyncSession):
        self.repo = ResumeRepository(db)

    async def upload_and_parse(self, file: UploadFile) -> ResumeUploadResponse:
        file_ext = Path(file.filename).suffix.lower().lstrip(".")  # "pdf" | "docx"
        resume_id = str(uuid.uuid4())
        stored_path = settings.RESUME_STORAGE_DIR / f"{resume_id}.{file_ext}"

        # 1. Save file to disk (streamed, capped at MAX_RESUME_SIZE_MB — size is
        #    already enforced at the API layer before this is called)
        contents = await file.read()
        stored_path.write_bytes(contents)

        # 2. Parse
        parsed = parse_resume(stored_path, file_ext)

        # 3. Persist DB record
        resume = Resume(
            id=resume_id,
            original_filename=file.filename,
            stored_path=str(stored_path),
            file_type=file_ext,
            parsed_skills_json=json.dumps(parsed["skills"]),
            parsed_experience_json=json.dumps(parsed["experience"]),
            parsed_education_json=json.dumps(parsed["education"]),
            raw_text=parsed["raw_text"],
            is_default=False,
        )
        saved = await self.repo.create(resume)

        # First resume uploaded becomes the default automatically
        existing = await self.repo.list_all()
        if len(existing) == 1:
            await self.repo.set_default(saved.id)
            saved.is_default = True

        return ResumeUploadResponse(
            id=saved.id,
            original_filename=saved.original_filename,
            file_type=saved.file_type,
            is_default=saved.is_default,
            created_at=saved.created_at,
            parsed=ParsedResumeSummary(
                skills=parsed["skills"],
                experience=parsed["experience"],
                education=parsed["education"],
            ),
        )

    async def get_default(self):
        """Return the default resume record, or None if none is set."""
        return await self.repo.get_default()

    async def list_resumes(self) -> list:
        from app.schemas.resume import ResumeResponse, ParsedResumeSummary
        rows = await self.repo.list_all()
        result = []
        for r in rows:
            result.append(ResumeResponse(
                id=r.id,
                original_filename=r.original_filename,
                file_type=r.file_type,
                is_default=r.is_default,
                created_at=r.created_at,
                parsed=ParsedResumeSummary(
                    skills=json.loads(r.parsed_skills_json or "[]"),
                    experience=json.loads(r.parsed_experience_json or "[]"),
                    education=json.loads(r.parsed_education_json or "[]"),
                ),
            ))
        return result

    async def set_default(self, resume_id: str) -> None:
        await self.repo.set_default(resume_id)

