from sqlalchemy import Boolean, Column, Integer, String

from app.database import Base


class BotState(Base):
    __tablename__ = "bot_state"

    id = Column(Integer, primary_key=True, default=1)
    status = Column(String, nullable=False, default="stopped")  # running | paused | stopped
    linkedin = Column(Boolean, nullable=False, default=True)
    indeed = Column(Boolean, nullable=False, default=True)
    glassdoor = Column(Boolean, nullable=False, default=True)
    dice = Column(Boolean, nullable=False, default=False)
    job_type = Column(String, nullable=False, default="full-time")
    location = Column(String, nullable=False, default="Remote")
    min_salary = Column(Integer, nullable=False, default=80000)
    apply_delay = Column(Integer, nullable=False, default=45)
