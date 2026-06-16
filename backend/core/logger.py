# ============================================================
# Structured Logging — Loguru
# ============================================================
import sys
from loguru import logger
from backend.config import LOGS_DIR

# Remove default handler
logger.remove()

# Console handler — colorized, short
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> — <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# File handler — full detail, rotation
logger.add(
    LOGS_DIR / "jobpilot_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} — {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
)

# Error-only log
logger.add(
    LOGS_DIR / "errors.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} — {message}",
    level="ERROR",
    rotation="5 MB",
    retention="90 days",
    encoding="utf-8",
)


def get_logger(name: str):
    """Get a named logger instance."""
    return logger.bind(name=name)
