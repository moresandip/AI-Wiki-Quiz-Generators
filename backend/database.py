import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        # Test the connection
        with engine.connect() as conn:
            pass
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        print(f"WARNING: Database connection failed. Ensure DATABASE_URL is correct in .env. Error: {e}")
        engine = None
        SessionLocal = None
else:
    engine = None
    SessionLocal = None

Base = declarative_base()

def get_db():
    if not SessionLocal:
        yield None
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
