import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend import database, models

def verify():
    print("Verifying init_db...")
    
    # Remove existing db if it exists to test creation
    if os.path.exists("quiz.db"):
        try:
            # os.remove("quiz.db") # Don't delete user's data if they have it locally
            pass
        except:
            pass
            
    try:
        database.init_db()
        print("init_db() called successfully.")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(database.engine)
        tables = inspector.get_table_names()
        print(f"Tables found: {tables}")
        
        if "quizzes" in tables:
            print("SUCCESS: 'quizzes' table exists.")
        else:
            print("FAILURE: 'quizzes' table NOT found.")
            
    except Exception as e:
        print(f"FAILURE: Error during verification: {e}")

if __name__ == "__main__":
    verify()
