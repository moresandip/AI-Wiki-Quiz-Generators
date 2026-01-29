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
# For Vercel, we now expect a persistent DATABASE_URL (Postgres)
# If not provided, we fall back to local SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Check if running on Vercel
    if os.getenv("VERCEL"):
        # Vercel filesystem is read-only except for /tmp
        # Note: Data will be lost when the function instance is recycled
        DB_PATH = "/tmp/quiz.db"
        DATABASE_URL = f"sqlite:///{DB_PATH}"
        print(f"Running on Vercel, using ephemeral DB at: {DB_PATH}")
        # Ensure the directory exists (though /tmp should always exist)
        try:
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        except Exception as e:
            print(f"Error creating DB directory: {e}")
    else:
        # Local development fallback
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, "quiz.db")
        DATABASE_URL = f"sqlite:///{DB_PATH}"

if SQL_AVAILABLE:
    # Check if SQLite is used, need check_same_thread=False
    connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

    try:
        print(f"Connecting to database at: {DATABASE_URL}")
        engine = create_engine(DATABASE_URL, connect_args=connect_args)
        # Test the connection
        if "sqlite" not in DATABASE_URL:
             # Optional: simpler test or skip for serverless if needed, 
             # but usually good to fail fast if DB is unreachable
             pass 
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
    except Exception as e:
        print(f"WARNING: Database connection failed. Ensure DATABASE_URL is correct. Error: {e}")
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

def init_db():
    """
    Ensure tables exist. This is idempotent and safe to call.
    Useful for serverless environments where /tmp might be wiped.
    """
    if SQL_AVAILABLE and engine:
        try:
            # Import models locally to ensure they are registered with Base.metadata
            # This avoids circular imports at the top level
            print(f"Initializing DB at {DATABASE_URL}")
            # Force import models to register them
            try:
                from . import models
                print("Imported models from .")
            except ImportError:
                import models
                print("Imported models directly")

            print(f"Registered tables before create: {Base.metadata.tables.keys()}")
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")


