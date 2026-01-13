import os
from dotenv import load_dotenv

load_dotenv()

try:
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    SQL_AVAILABLE = True
except ImportError:
    SQL_AVAILABLE = False
    Base = object # Dummy base to prevent errors
    SessionLocal = None
    engine = None

# Check if running on Vercel (or any read-only environment)
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    # Use /tmp directory for SQLite in serverless environments
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/quiz.db")
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quiz.db")

if SQL_AVAILABLE:
    try:
        # Check if SQLite is used, need check_same_thread=False
        connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
        engine = create_engine(DATABASE_URL, connect_args=connect_args)
        # Test the connection
        with engine.connect() as conn:
            pass
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
    except Exception as e:
        print(f"WARNING: Database connection failed. Ensure DATABASE_URL is correct in .env. Error: {e}")
        engine = None
        SessionLocal = None
        Base = object
else:
    engine = None
    SessionLocal = None
    if SQL_AVAILABLE:
        Base = declarative_base()
    else:
         Base = object

def get_db():
    if not SessionLocal:
        yield None
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
