import logging
from typing import Optional
from .config import settings
from .constants import LOG_FORMAT


def configure_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    handler = logging.StreamHandler()
    handler.setLevel(settings.log_level)

    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)

    if not root_logger.handlers:
        root_logger.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name)
