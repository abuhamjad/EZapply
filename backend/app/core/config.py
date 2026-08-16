"""
Centralized application settings.
Loaded once as a singleton `settings` object, imported everywhere else.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/


class Settings(BaseSettings):
    APP_NAME: str = "EZApply Backend"
    API_V1_PREFIX: str = "/api/v1"

    # SQLite DB lives inside backend/app.db
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'app.db'}"

    # Where uploaded resumes are stored on disk
    RESUME_STORAGE_DIR: Path = BASE_DIR / "storage" / "resumes"
    MAX_RESUME_SIZE_MB: int = 10
    ALLOWED_RESUME_EXTENSIONS: tuple[str, ...] = (".pdf", ".docx", ".doc", ".txt")

    # CORS - React dev server / Electron/Tauri origin
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "tauri://localhost"]

    # Bot defaults
    DEFAULT_APPLICATION_LIMIT: int = 25
    PLAYWRIGHT_HEADLESS: bool = False  # Set to True in .env for headless/CI environments

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
settings.RESUME_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
