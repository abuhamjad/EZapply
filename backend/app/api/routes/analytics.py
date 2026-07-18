from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.repositories import EZApplyRepository
from app.schemas.analytics import AnalyticsSummaryResponse, ApplicationsResponse, PlatformsResponse
from app.services.analytics_service import AnalyticsService


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/applications", response_model=ApplicationsResponse)
def get_applications(database: Session = Depends(get_db)) -> dict:
    return {"data": AnalyticsService(EZApplyRepository(database)).applications_by_day()}


@router.get("/platforms", response_model=PlatformsResponse)
def get_platforms(database: Session = Depends(get_db)) -> dict:
    return {"data": AnalyticsService(EZApplyRepository(database)).platforms()}


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(database: Session = Depends(get_db)) -> dict:
    return AnalyticsService(EZApplyRepository(database)).summary()
