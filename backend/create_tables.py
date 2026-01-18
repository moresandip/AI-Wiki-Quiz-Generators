#!/usr/bin/env python3
"""
Script to create database tables for the AI Wiki Quiz Generator.
Run this script to initialize the database tables.
"""

import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(__file__))

try:
    from database import engine, SQL_AVAILABLE
    from models import Base

    if SQL_AVAILABLE and engine:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    else:
        print("Database not configured. Set DATABASE_URL environment variable.")

except Exception as e:
    print(f"Error creating tables: {e}")
    sys.exit(1)
