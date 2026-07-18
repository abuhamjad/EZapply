from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.constants import APP_NAME, API_VERSION
from app.api import api_router
from app.database.engine import initialize_database

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    logger.info("Local database initialized")
    yield

app = FastAPI(
    title=APP_NAME,
    version=API_VERSION,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS — allow the Vite dev server to reach the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:1420",
        "http://localhost:1420",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

logger.info(f"{APP_NAME} backend started (v{API_VERSION})")
