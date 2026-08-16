import asyncio
import subprocess
import sys
import logging
from contextlib import asynccontextmanager

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.database.connection import init_db

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    loop = asyncio.get_running_loop()
    logger.info("Lifespan event loop type: %s, policy: %s", type(loop).__name__, type(asyncio.get_event_loop_policy()).__name__)
    await init_db()  # creates SQLite tables on first run
    
    # Ensure Playwright browsers are installed
    logger.info("Checking Playwright browser installation...")
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Playwright browsers: {e.stderr.decode()}")
        raise RuntimeError("Playwright Chromium browser not installed. Please run `playwright install chromium` manually.") from e

    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:1420",
        "http://127.0.0.1:1420",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "tauri://localhost",
        "*",  # WARNING: Lock this down before any non-localhost deployment!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Support both /api (frontend client.ts default) and /api/v1 (REST standards)
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
