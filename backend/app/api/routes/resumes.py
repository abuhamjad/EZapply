from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.connection import get_db
from app.schemas.resume import ResumeResponse, ResumeUploadResponse
from app.services.resume import ResumeService

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile, db: AsyncSession = Depends(get_db)):
    # --- Validation (API layer's only job: shape/size/type checks) ---
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_RESUME_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.MAX_RESUME_SIZE_MB}MB limit")
    await file.seek(0)

    return await ResumeService(db).upload_and_parse(file)


@router.get("", response_model=list[ResumeResponse])
async def list_resumes(db: AsyncSession = Depends(get_db)):
    return await ResumeService(db).list_resumes()


@router.put("/{resume_id}/default", status_code=status.HTTP_204_NO_CONTENT)
async def set_default_resume(resume_id: str, db: AsyncSession = Depends(get_db)):
    await ResumeService(db).set_default(resume_id)
