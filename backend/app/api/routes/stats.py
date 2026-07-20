from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.api import AnalyticsOut, DashboardOut
from app.services import stats

router = APIRouter(tags=["stats"])


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    return stats.get_dashboard(db)


@router.get("/analytics", response_model=AnalyticsOut)
def analytics(db: Session = Depends(get_db)):
    return stats.get_analytics(db)
