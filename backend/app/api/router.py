from fastapi import APIRouter

from app.api.routes import (
    analytics,
    applications,
    bot,
    dashboard,
    resumes,
    saved_info,
    stats,
)

api_router = APIRouter()

api_router.include_router(saved_info.router)
api_router.include_router(resumes.router)
api_router.include_router(bot.router)
api_router.include_router(applications.router)
api_router.include_router(stats.router)
api_router.include_router(dashboard.router)
api_router.include_router(analytics.router)
