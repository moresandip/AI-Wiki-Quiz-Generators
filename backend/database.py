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
# Check if running on Vercel (or any read-only environment)
if os.environ.get("VERCEL"):
    # Vercel has a read-only filesystem, so we use /tmp for the database.
    # This database will be ephemeral, new for each invocation.
    DATABASE_URL = "sqlite:////tmp/quiz.db"
else:
    # For local development, use a file-based SQLite database.
    # Use absolute path to ensure it works regardless of CWD
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "quiz.db")
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

if SQL_AVAILABLE:
    # Check if SQLite is used, need check_same_thread=False
    connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

    # For Vercel, skip connection test as /tmp might not be immediately writable
    if os.environ.get("VERCEL"):
        try:
            engine = create_engine(DATABASE_URL, connect_args=connect_args)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            Base = declarative_base()
            print("Engine created for Vercel")
        except Exception as e:
            print(f"Failed to create engine for Vercel: {e}")
            engine = None
            SessionLocal = None
            Base = object
    else:
        try:
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

# Create tables on module import (for serverless environments)
# REMOVED: Automatic table creation on import caused circular dependency issues.
# Tables should be created explicitly in main.py startup event or via create_tables.py script.

