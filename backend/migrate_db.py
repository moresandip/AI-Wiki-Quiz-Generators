"""
Database migration script to add missing user_answers column to quizzes table.
This fixes the sqlite3.OperationalError: no such column: quizzes.user_answers
"""
import sqlite3
import os
import sys

def migrate_database(db_path='quiz.db'):
    """Add user_answers column to quizzes table if it doesn't exist"""
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. It will be created on first quiz generation.")
        return
    
    print(f"Migrating database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(quizzes)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns: {column_names}")
        
        # Check if user_answers column exists
        if 'user_answers' not in column_names:
            print("Adding user_answers column...")
            cursor.execute("ALTER TABLE quizzes ADD COLUMN user_answers TEXT")
            conn.commit()
            print("✓ Successfully added user_answers column")
        else:
            print("✓ user_answers column already exists")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(quizzes)")
        columns = cursor.fetchall()
        print(f"\nUpdated schema:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Get database path from command line or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'quiz.db'
    migrate_database(db_path)
