import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Import local modules
from . import models, schemas, scraper, llm, database

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
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables if they don't exist
# Create tables on startup (essential for Vercel/SQLite)
@app.on_event("startup")
async def startup_event():
    if database.SQL_AVAILABLE and database.engine:
        models.Base.metadata.create_all(bind=database.engine)
        logger.info("Database tables created (if not existed).")

@app.get("/")
def read_root():
    return {"message": "AI Wiki Quiz Generator API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/quiz", response_model=schemas.QuizResponse)
def generate_quiz(request: schemas.QuizRequest, db: Session = Depends(get_db)):
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
    if not db:
        return []
    quizzes = db.query(models.Quiz).order_by(models.Quiz.created_at.desc()).offset(skip).limit(limit).all()
    return quizzes

@app.get("/api/quiz/{quiz_id}", response_model=schemas.QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
