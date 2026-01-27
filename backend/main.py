import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Import local modules
# Import local modules
import sys
from pathlib import Path

# Add the project root to sys.path to allow absolute imports
# This is necessary for Windows/Uvicorn reloading to work correctly
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from backend import models, schemas, scraper, llm, database
except ImportError:
    # Fallback if running directly from backend dir
    import models, schemas, scraper, llm, database

# Create tables if they don't exist (for serverless environments like Vercel)
# Moved to startup event to ensure models are loaded first

# Import create_tables function
try:
    from create_tables import create_tables
except ImportError:
    from backend.create_tables import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backend_debug.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Wiki Quiz Generator")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    # Ensure tables exist (lazy check for serverless SQLite)
    database.init_db()
    
    if database.SessionLocal:
        db = database.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None

# Create tables if they don't exist
# Create tables on startup (essential for Vercel/SQLite)
@app.on_event("startup")
async def startup_event():
    # Ensure tables exist
    create_tables()
    logger.info("Database tables created (if not existed).")

@app.get("/")
def read_root():
    return {"message": "AI Wiki Quiz Generator API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/quiz", response_model=schemas.QuizResponse)
def generate_quiz(request: schemas.QuizRequest, db: Session = Depends(get_db)):
    # Ensure tables exist
    # Ensure tables exist - REMOVED redundant check


    logger.info(f"Received quiz request for URL: {request.url}")

    try:
        # 1. Scrape Wikipedia
        logger.info("Scraping Wikipedia...")
        scraped_data = scraper.scrape_wikipedia(request.url)
        logger.info(f"Scraping successful. Title: {scraped_data.get('title')}")
        
        # 2. Generate Quiz using LLM
        logger.info("Generating quiz with LLM...")
        quiz_data = llm.generate_quiz_data(scraped_data)
        logger.info("Quiz generation successful")
        
        # 3. Save to database (if available)
        db_quiz = None
        if db:
            try:
                db_quiz = models.Quiz(
                    url=request.url,
                    title=quiz_data.get("title"),
                    summary=quiz_data.get("summary"),
                    data=quiz_data
                )
                db.add(db_quiz)
                db.commit()
                db.refresh(db_quiz)
                logger.info(f"Saved quiz to database with ID: {db_quiz.id}")
            except Exception as e:
                logger.error(f"Failed to save to database: {e}")
                # Continue even if DB save fails
        
        return {
            "id": db_quiz.id if db_quiz else None,
            "url": request.url,
            "title": quiz_data.get("title"),
            "summary": quiz_data.get("summary"),
            "data": quiz_data,
            "created_at": db_quiz.created_at if db_quiz else None
        }

    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quizzes", response_model=List[schemas.QuizResponse])
def get_recent_quizzes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Ensure tables exist
    # Ensure tables exist - REMOVED redundant check

    logger.info(f"get_recent_quizzes called with skip={skip}, limit={limit}")
    if not db:
        logger.info("No database connection")
        return []
    try:
        quizzes = db.query(models.Quiz).order_by(models.Quiz.created_at.desc()).offset(skip).limit(limit).all()
        logger.info(f"Found {len(quizzes)} quizzes")
        return quizzes
    except Exception as e:
        logger.error(f"Error querying quizzes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quiz/{quiz_id}", response_model=schemas.QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    # Ensure tables exist
    # Ensure tables exist - REMOVED redundant check


    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@app.delete("/api/quiz/{quiz_id}")
def delete_quiz(quiz_id: int, db: Session = Depends(get_db)):
    # Ensure tables exist
    # Ensure tables exist - REMOVED redundant check


    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    db.delete(quiz)
    db.commit()
    logger.info(f"Deleted quiz with ID: {quiz_id}")
    return {"message": "Quiz deleted successfully"}

@app.put("/api/quiz/{quiz_id}/save-results")
def save_quiz_results(quiz_id: int, request: Dict[str, Any], db: Session = Depends(get_db)):
    # Ensure tables exist
    # Ensure tables exist - REMOVED redundant check


    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Update quiz data with user answers
    user_answers = request.get("user_answers", {})
    if quiz.data:
        quiz.data["user_answers"] = user_answers
    else:
        quiz.data = {"user_answers": user_answers}

    db.commit()
    db.refresh(quiz)
    logger.info(f"Saved results for quiz ID: {quiz_id}")
    return {"message": "Results saved successfully", "quiz": quiz}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
