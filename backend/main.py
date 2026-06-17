# ============================================================
# FastAPI Main — JobPilot AI Backend Server
# ============================================================
import sys
import os
import json

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in path (for importing existing bot modules)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import API_HOST, API_PORT
from backend.database.engine import init_db, SessionLocal
from backend.database.models import Setting, User, Profile
from backend.api.router import router
from backend.services.encryption import encryption_service
from backend.services.ai.claude_service import claude_service
from backend.core.logger import get_logger

log = get_logger("main")


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialize database, load saved credentials, configure AI."""
    log.info("JobPilot AI Backend starting...")

    # Initialize database
    init_db()

    # Create default user + profile if none exist
    db = SessionLocal()
    try:
        if not db.query(User).first():
            user = User(email="user@local", display_name="User")
            db.add(user)
            db.commit()
            db.refresh(user)
            profile = Profile(
                user_id=user.id, name="Default Profile",
                email="", phone="", experience_level="Entry",
            )
            db.add(profile)
            db.commit()
            log.info("Default user + profile created")

        # Load Bedrock API key from settings
        api_key_setting = db.query(Setting).filter(Setting.key == "bedrock_api_key").first()
        if api_key_setting and api_key_setting.value:
            decrypted_key = encryption_service.decrypt(api_key_setting.value)
            if decrypted_key:
                region_setting = db.query(Setting).filter(Setting.key == "bedrock_region").first()
                region = region_setting.value if region_setting else "us-east-1"
                claude_service.configure(decrypted_key, region)
                log.info("Bedrock Claude configured from saved credentials")
            else:
                log.warning("Bedrock API key decryption failed")
        else:
            log.info("No Bedrock API key configured — AI features disabled")
    finally:
        db.close()

    log.info(f"Server ready: http://{API_HOST}:{API_PORT}")
    log.info(f"API Docs: http://{API_HOST}:{API_PORT}/docs")

    yield  # Application runs here

    log.info("JobPilot AI Backend shutting down...")


app = FastAPI(
    title="JobPilot AI",
    description="AI-powered Job Application Assistant",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow Electron renderer and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(router)

# Serve frontend static files (React build output)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "dist")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    print("""
╔══════════════════════════════════════════════╗
║         JobPilot AI — Desktop Backend        ║
║──────────────────────────────────────────────║
║  API:  http://127.0.0.1:8420                 ║
║  Docs: http://127.0.0.1:8420/docs            ║
║  WS:   ws://127.0.0.1:8420/api/ws            ║
╚══════════════════════════════════════════════╝
""")
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info",
    )
