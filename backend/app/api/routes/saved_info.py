from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.repositories import EZApplyRepository
from app.schemas.saved_info import (
    CoverLetterTemplate,
    CreateTemplateRequest,
    KeywordsResponse,
    KeywordsUpdateRequest,
    ProfileResponse,
    ProfileUpdateRequest,
    ResumeResponse,
    ResumesResponse,
    TemplatesResponse,
)
from app.services.saved_info_service import SavedInfoService


router = APIRouter(prefix="/api/saved-info", tags=["saved-info"])


def _service(database: Session) -> SavedInfoService:
    return SavedInfoService(EZApplyRepository(database))


@router.get("/profile", response_model=ProfileResponse)
def get_profile(database: Session = Depends(get_db)) -> dict:
    return _service(database).profile()


@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    request: ProfileUpdateRequest,
    database: Session = Depends(get_db),
) -> dict:
    fields = [field.model_dump() for field in request.fields]
    return _service(database).update_profile(fields, request.skills)


@router.get("/keywords", response_model=KeywordsResponse)
def get_keywords(database: Session = Depends(get_db)) -> dict:
    return _service(database).keywords()


@router.put("/keywords", response_model=KeywordsResponse)
def update_keywords(
    request: KeywordsUpdateRequest,
    database: Session = Depends(get_db),
) -> dict:
    return _service(database).update_keywords(
        request.saved_keywords, request.excluded_keywords
    )


@router.get("/templates", response_model=TemplatesResponse)
def get_templates(database: Session = Depends(get_db)) -> dict:
    return {"templates": _service(database).templates()}


@router.post("/templates", response_model=CoverLetterTemplate)
def create_template(
    request: CreateTemplateRequest,
    database: Session = Depends(get_db),
) -> dict:
    return _service(database).create_template(request.name, request.content)


@router.delete("/templates/{template_id}", status_code=204)
def delete_template(template_id: int, database: Session = Depends(get_db)) -> None:
    if not _service(database).delete_template(template_id):
        raise HTTPException(status_code=404, detail="Template not found.")


@router.get("/resumes", response_model=ResumesResponse)
def get_resumes(database: Session = Depends(get_db)) -> dict:
    return {"resumes": _service(database).resumes()}


@router.post("/resumes", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    database: Session = Depends(get_db),
) -> dict:
    return await _service(database).upload_resume(file)


@router.delete("/resumes/{resume_id}", status_code=204)
def delete_resume(resume_id: int, database: Session = Depends(get_db)) -> None:
    if not _service(database).delete_resume(resume_id):
        raise HTTPException(status_code=404, detail="Resume not found.")
