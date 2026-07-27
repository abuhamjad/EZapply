from enum import Enum


class BotRunStatus(str, Enum):
    STARTED = "STARTED"
    RUNNING = "RUNNING"
    PAUSED_NEEDS_INPUT = "PAUSED_NEEDS_INPUT"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class Platform(str, Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
