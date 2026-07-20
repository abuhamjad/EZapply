from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    company = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    status = Column(String, nullable=False, default="sent")
    applied_at = Column(DateTime, nullable=False, default=datetime.utcnow)
