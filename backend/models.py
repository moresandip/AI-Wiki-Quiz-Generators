from .database import Base, SQL_AVAILABLE, DATABASE_URL

if SQL_AVAILABLE:
    from sqlalchemy import Column, Integer, String, Text, DateTime
    from sqlalchemy.sql import func

    # Determine JSON column type based on database
    if "sqlite" in DATABASE_URL:
        JSONType = Text
    else:
        try:
            from sqlalchemy.dialects.postgresql import JSON
            JSONType = JSON
        except ImportError:
            # Fallback if psycopg2 not installed or other DB
            JSONType = Text

    class Quiz(Base):
        __tablename__ = "quizzes"

        id = Column(Integer, primary_key=True, index=True)
        url = Column(String, unique=False, index=True, nullable=False)
        title = Column(String, nullable=True)
        summary = Column(Text, nullable=True)
        # Stores the full JSON response (quiz questions, related topics, entities, etc.)
        data = Column(JSONType, nullable=False)
        user_answers = Column(JSONType, nullable=True)  # Store user answers as JSON
        created_at = Column(DateTime(timezone=True), server_default=func.now())
else:
    # Dummy class to prevent import errors if SQL is not available
    class Quiz:
        pass
