from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Database session dependency for route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
