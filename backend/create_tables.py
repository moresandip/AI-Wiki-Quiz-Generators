#!/usr/bin/env python3
"""
Script to create database tables.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path so we can import modules
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database import SQL_AVAILABLE, engine, Base
try:
    from models import Quiz
except ImportError:
    from backend.models import Quiz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables"""
    if not SQL_AVAILABLE or not engine:
        logger.info("Database not available, skipping table creation")
        return

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()
