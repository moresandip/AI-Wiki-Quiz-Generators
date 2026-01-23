#!/usr/bin/env python3
"""
Database migration script to add missing columns to the quizzes table.
This script handles adding the user_answers column that was missing from the database schema.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path so we can import modules
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from backend.database import SQL_AVAILABLE, engine, SessionLocal
    from backend.models import Quiz
except ImportError:
    try:
        from database import SQL_AVAILABLE, engine, SessionLocal
        from models import Quiz
    except ImportError:
        # Fallback
        from .database import SQL_AVAILABLE, engine, SessionLocal
        from .models import Quiz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Add missing columns to the quizzes table"""
    if not SQL_AVAILABLE:
        logger.info("SQL not available, skipping migration")
        return

    try:
        # Check if user_answers column exists
        from sqlalchemy import inspect
        inspector = inspect(engine)

        # Get existing columns
        existing_columns = [col['name'] for col in inspector.get_columns('quizzes')]

        if 'user_answers' not in existing_columns:
            logger.info("Adding user_answers column to quizzes table...")

            # For SQLite, we need to recreate the table
            if "sqlite" in str(engine.url):
                # SQLite doesn't support ALTER TABLE ADD COLUMN with constraints easily
                # We'll use a different approach - recreate the table
                logger.info("SQLite detected, recreating table with new schema...")

                # Create a backup table
                with engine.connect() as conn:
                    conn.execute("CREATE TABLE quizzes_backup AS SELECT * FROM quizzes")
                    conn.execute("DROP TABLE quizzes")
                    conn.commit()

                # Recreate the table with the new schema
                Quiz.__table__.create(engine)

                # Restore data
                conn.execute("""
                    INSERT INTO quizzes (id, url, title, summary, data, created_at)
                    SELECT id, url, title, summary, data, created_at FROM quizzes_backup
                """)
                conn.execute("DROP TABLE quizzes_backup")
                conn.commit()

                logger.info("Migration completed successfully!")
            else:
                # For other databases, use ALTER TABLE
                from sqlalchemy import text
                with engine.connect() as conn:
                    # Determine JSON column type
                    if "postgresql" in str(engine.url):
                        json_type = "JSONB"
                    else:
                        json_type = "TEXT"

                    conn.execute(text(f"ALTER TABLE quizzes ADD COLUMN user_answers {json_type}"))
                    conn.commit()
                    logger.info("Added user_answers column successfully!")

        else:
            logger.info("user_answers column already exists, no migration needed")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_database()
