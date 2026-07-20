from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.models import CoverLetterTemplate, Keyword
from app.schemas.api import (
    KeywordCreate,
    KeywordOut,
    SavedInfoOut,
    TemplateCreate,
    TemplateOut,
)

router = APIRouter(prefix="/saved-info", tags=["saved-info"])


@router.get("", response_model=SavedInfoOut)
def get_saved_info(db: Session = Depends(get_db)):
    keywords = db.query(Keyword).order_by(Keyword.id).all()
    templates = (
        db.query(CoverLetterTemplate).order_by(CoverLetterTemplate.id).all()
    )
    return SavedInfoOut(
        saved_keywords=[k for k in keywords if k.kind == "include"],
        excluded_keywords=[k for k in keywords if k.kind == "exclude"],
        cover_letter_templates=templates,
    )


@router.post("/keywords", response_model=KeywordOut, status_code=201)
def add_keyword(payload: KeywordCreate, db: Session = Depends(get_db)):
    keyword = Keyword(text=payload.text, kind=payload.kind)
    db.add(keyword)
    db.commit()
    db.refresh(keyword)
    return keyword


@router.delete("/keywords/{keyword_id}", status_code=204)
def delete_keyword(keyword_id: int, db: Session = Depends(get_db)):
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if keyword is None:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(keyword)
    db.commit()


@router.post("/templates", response_model=TemplateOut, status_code=201)
def add_template(payload: TemplateCreate, db: Session = Depends(get_db)):
    template = CoverLetterTemplate(name=payload.name)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.delete("/templates/{template_id}", status_code=204)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = (
        db.query(CoverLetterTemplate)
        .filter(CoverLetterTemplate.id == template_id)
        .first()
    )
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
