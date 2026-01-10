from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from database import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    # Stores the full JSON response (quiz questions, related topics, entities, etc.)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
