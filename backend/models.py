try:
    from .database import Base, SQL_AVAILABLE, DATABASE_URL
except ImportError:
    from database import Base, SQL_AVAILABLE, DATABASE_URL

if SQL_AVAILABLE:
    from sqlalchemy import Column, Integer, String, Text, DateTime
    from sqlalchemy.types import TypeDecorator
    from sqlalchemy.sql import func
    import json

    class JSONEncodedDict(TypeDecorator):
        """Represents an immutable structure as a json-encoded string."""
        impl = Text

        def process_bind_param(self, value, dialect):
            if value is None:
                return None
            return json.dumps(value)

        def process_result_value(self, value, dialect):
            if value is None:
                return None
            return json.loads(value)

    # Use JSONEncodedDict for all databases to ensure consistency and SQLite support
    JSONType = JSONEncodedDict

    class Quiz(Base):
        __tablename__ = "quizzes"
        __table_args__ = {'extend_existing': True}

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
