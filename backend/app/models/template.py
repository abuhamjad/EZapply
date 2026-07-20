from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class CoverLetterTemplate(Base):
    __tablename__ = "cover_letter_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    last_edited = Column(DateTime, nullable=False, default=datetime.utcnow)
