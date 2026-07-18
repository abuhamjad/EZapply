from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.saved_info import router as saved_info_router
from app.api.routes.automation import router as automation_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="")
api_router.include_router(dashboard_router)
api_router.include_router(analytics_router)
api_router.include_router(saved_info_router)
api_router.include_router(automation_router)
