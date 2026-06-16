# ============================================================
# Database Engine — SQLite with SQLAlchemy
# ============================================================
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.config import DATABASE_PATH
from backend.core.logger import get_logger

log = get_logger("database")

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

# Enable WAL mode for better concurrent reads
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Session:
    """FastAPI dependency — yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    from backend.database.models import Base
    Base.metadata.create_all(bind=engine)
    log.info(f"Database initialized: {DATABASE_PATH}")
