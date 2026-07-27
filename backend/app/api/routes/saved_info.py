from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.schemas.saved_info import (
    KeywordCreate,
    KeywordItem,
    SavedInfoResponse,
    SavedInfoUpdate,
    TemplateCreate,
    TemplateItem,
)
from app.services.saved_info import SavedInfoService

router = APIRouter(prefix="/saved-info", tags=["Saved Info"])


@router.get("", response_model=SavedInfoResponse)
async def get_saved_info(db: AsyncSession = Depends(get_db)):
    return await SavedInfoService(db).get()


@router.put("", response_model=SavedInfoResponse)
async def update_saved_info(payload: SavedInfoUpdate, db: AsyncSession = Depends(get_db)):
    return await SavedInfoService(db).update(payload)


@router.post("/keywords", response_model=KeywordItem, status_code=status.HTTP_201_CREATED)
async def add_keyword(payload: KeywordCreate, db: AsyncSession = Depends(get_db)):
    return await SavedInfoService(db).add_keyword(payload.text, payload.kind)


@router.delete("/keywords/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(keyword_id: int, db: AsyncSession = Depends(get_db)):
    await SavedInfoService(db).delete_keyword(keyword_id)


@router.post("/templates", response_model=TemplateItem, status_code=status.HTTP_201_CREATED)
async def add_template(payload: TemplateCreate, db: AsyncSession = Depends(get_db)):
    return await SavedInfoService(db).add_template(payload.name)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: int, db: AsyncSession = Depends(get_db)):
    await SavedInfoService(db).delete_template(template_id)
