
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend import database, models
    from sqlalchemy import inspect
    
    print(f"Database URL: {database.DATABASE_URL}")
    
    if database.engine:
        inspector = inspect(database.engine)
        tables = inspector.get_table_names()
        print(f"Existing tables: {tables}")
        
        if "quizzes" in tables:
            print("Table 'quizzes' exists.")
        else:
            print("Table 'quizzes' DOES NOT exist.")
            
            # Try to create it
            print("Attempting to create tables...")
            models.Base.metadata.create_all(bind=database.engine)
            
            tables_after = inspector.get_table_names()
            print(f"Tables after creation: {tables_after}")
            
            if "quizzes" in tables_after:
                print("Successfully created 'quizzes' table.")
            else:
                print("FAILED to create 'quizzes' table.")
                
    else:
        print("Database engine is None.")

except Exception as e:
    print(f"Error: {e}")
