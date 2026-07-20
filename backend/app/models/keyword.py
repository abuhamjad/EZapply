from sqlalchemy import Column, Integer, String

from app.database import Base


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    kind = Column(String, nullable=False, default="include")  # include | exclude
