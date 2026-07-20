from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.constants import API_VERSION, APP_NAME
from app.core.logging import configure_logging, get_logger
from app.database import Base, SessionLocal, engine
from app.database.seed import seed_db
from app import models  # noqa: F401  (register models with Base.metadata)

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
    logger.info(f"{APP_NAME} backend started (v{API_VERSION})")
    yield


app = FastAPI(
    title=APP_NAME,
    version=API_VERSION,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1420",
        "http://127.0.0.1:1420",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
