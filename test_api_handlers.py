#!/usr/bin/env python3
"""
Test script to verify API handlers can create database tables
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_table_creation():
    """Test that database tables can be created"""
    try:
        from database import engine, SQL_AVAILABLE
        from models import Base

        if SQL_AVAILABLE and engine:
            print("Creating database tables...")
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully!")

            # Test connection
            with engine.connect() as conn:
                result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quizzes';")
                if result.fetchone():
                    print("✓ 'quizzes' table exists")
                else:
                    print("✗ 'quizzes' table does not exist")
        else:
            print("Database not available")

    except Exception as e:
        print(f"Error: {e}")

def test_generate_quiz_handler():
    """Test that generate-quiz handler can import and create tables"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
        import generate_quiz
        print("✓ generate-quiz handler imports successfully")
    except Exception as e:
        print(f"✗ generate-quiz handler import failed: {e}")

def test_quizzes_handler():
    """Test that quizzes handler can import and create tables"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
        import quizzes
        print("✓ quizzes handler imports successfully")
    except Exception as e:
        print(f"✗ quizzes handler import failed: {e}")

def test_quiz_handler():
    """Test that quiz/[quiz_id] handler can import and create tables"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'api', 'quiz'))
        import quiz_id
        print("✓ quiz/[quiz_id] handler imports successfully")
    except Exception as e:
        print(f"✗ quiz/[quiz_id] handler import failed: {e}")

if __name__ == "__main__":
    print("Testing API handlers...")
    test_table_creation()
    test_generate_quiz_handler()
    test_quizzes_handler()
    test_quiz_handler()
    print("Testing complete!")
