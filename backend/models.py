from database import Base, SQL_AVAILABLE

if SQL_AVAILABLE:
    from sqlalchemy import Column, Integer, String, Text, DateTime
    from sqlalchemy.dialects.postgresql import JSON
    from sqlalchemy.sql import func
    
    class Quiz(Base):
        __tablename__ = "quizzes"

        id = Column(Integer, primary_key=True, index=True)
        url = Column(String, unique=False, index=True, nullable=False)
        title = Column(String, nullable=True)
        summary = Column(Text, nullable=True)
        # Stores the full JSON response (quiz questions, related topics, entities, etc.)
        data = Column(JSON, nullable=False)
        user_answers = Column(JSON, nullable=True)  # Store user answers as JSON
        created_at = Column(DateTime(timezone=True), server_default=func.now())
else:
    # Dummy class to prevent import errors if SQL is not available
    class Quiz:
        pass
