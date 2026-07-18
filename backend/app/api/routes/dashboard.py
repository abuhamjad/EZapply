from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.repositories import EZApplyRepository
from app.schemas.dashboard import DashboardStatsResponse, DashboardSummaryResponse
from app.services.dashboard_service import DashboardService


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(database: Session = Depends(get_db)) -> dict:
    return DashboardService(EZApplyRepository(database)).summary()


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(database: Session = Depends(get_db)) -> dict:
    return DashboardService(EZApplyRepository(database)).stats()
