import os
import sys
import traceback

# Add current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def log(msg):
    with open("db_test_log.txt", "a") as f:
        f.write(msg + "\n")

if __name__ == "__main__":
    try:
        # Clear log file
        with open("db_test_log.txt", "w") as f:
            f.write("Starting test_db_connection.py\n")

        from dotenv import load_dotenv
        load_dotenv()
        log("Loaded dotenv")

        try:
            from database import SessionLocal, engine, SQL_AVAILABLE
            from models import Base, Quiz
            log(f"Imported database. SQL_AVAILABLE: {SQL_AVAILABLE}")
        except ImportError as e:
            log(f"ImportError: {e}")
            SQL_AVAILABLE = False
        except Exception as e:
            log(f"Import Exception: {e}")
            log(traceback.format_exc())
            SQL_AVAILABLE = False

        if not SQL_AVAILABLE:
            log("SQLAlchemy not available. Exiting.")
            sys.exit(0)

        log(f"Database URL: {os.getenv('DATABASE_URL')}")
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        log("Tables created (or exist).")
        
        # Try to create a session
        db = SessionLocal()
        log("Session created.")
        
        # Try to insert a dummy quiz
        new_quiz = Quiz(
            url="http://test.com",
            title="Test Quiz",
            summary="Test Summary",
            data={"quiz": []}
        )
        db.add(new_quiz)
        db.commit()
        db.refresh(new_quiz)
        log(f"Successfully inserted quiz with ID: {new_quiz.id}")
        
        # Clean up
        db.delete(new_quiz)
        db.commit()
        log("Successfully deleted test quiz.")
        db.close()
        
    except Exception as e:
        log(f"Top Level Error: {e}")
        log(traceback.format_exc())
        sys.exit(1)
