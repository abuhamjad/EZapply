from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.constants import APP_NAME, API_VERSION
from app.api import api_router

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=APP_NAME,
    version=API_VERSION,
    debug=settings.debug,
)

app.include_router(api_router)

logger.info(f"{APP_NAME} backend started (v{API_VERSION})")
