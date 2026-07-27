from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.application_repository import ApplicationRepository
from app.schemas.application import ApplicationResponse

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await ApplicationRepository(db).list_recent(limit=limit)
