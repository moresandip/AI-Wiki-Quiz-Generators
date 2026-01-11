import sys
import os
import traceback

LOG_FILE = "simple_log.txt"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

if __name__ == "__main__":
    # Clear log
    with open(LOG_FILE, "w") as f:
        f.write("Starting simple_test.py (CRUD)\n")

    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        import database
        from models import Base, Quiz
        
        log(f"Database module imported. SQL_AVAILABLE: {database.SQL_AVAILABLE}")
        
        if not database.SQL_AVAILABLE:
            log("SQLAlchemy not available. Exiting.")
            sys.exit(0)

        # Create tables
        log("Creating tables...")
        database.Base.metadata.create_all(bind=database.engine)
        log("Tables created.")

        # Create session
        log("Creating session...")
        db = database.SessionLocal()
        log("Session created.")

        # Insert
        log("Inserting quiz...")
        new_quiz = Quiz(
            url="http://test-crud.com",
            title="Test CRUD Quiz",
            summary="Test Summary",
            data={"quiz": []}
        )
        db.add(new_quiz)
        db.commit()
        db.refresh(new_quiz)
        log(f"Inserted quiz with ID: {new_quiz.id}")

        # Verify
        q = db.query(Quiz).filter(Quiz.id == new_quiz.id).first()
        if q:
            log(f"Verified quiz exists: {q.title}")
        else:
            log("ERROR: Quiz not found after insert!")

        # Delete
        log("Deleting quiz...")
        db.delete(new_quiz)
        db.commit()
        log("Deleted quiz.")
        
        db.close()
        log("Test Complete Success")

    except Exception as e:
        log(f"Error: {e}")
        log(traceback.format_exc())
