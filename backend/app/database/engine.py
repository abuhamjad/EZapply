from sqlalchemy import create_engine
from app.core.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
)


def initialize_database() -> None:
    """Create the local SQLite schema on first application start."""
    # Import entities before metadata creation so every table is registered.
    import app.models  # noqa: F401
    from app.database.base import Base

    Base.metadata.create_all(bind=engine)
