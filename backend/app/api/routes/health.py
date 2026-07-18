from fastapi import APIRouter
from app.core.constants import API_VERSION

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {"status": "ok", "version": API_VERSION}
