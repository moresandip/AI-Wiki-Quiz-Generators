from typing import Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
try:
    from sqlalchemy.orm import Session
except ImportError:
    Session = None
from database import get_db, SQL_AVAILABLE
from models import Quiz
from schemas import QuizRequest, QuizResponse, SaveResultsRequest
from scraper import scrape_wikipedia
from llm import generate_quiz_data
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="AI Wiki Quiz Generator", version="1.0.0")

from fastapi.middleware.cors import CORSMiddleware

# CORS configuration - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Serve frontend
static_files_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=static_files_path), name="static")


@app.on_event("startup")
def startup_event():
    try:
        from database import engine
        if engine:
            import models
            models.Base.metadata.create_all(bind=engine)
            print("Database tables created successfully.")
        else:
            print("WARNING: Database not configured. Set DATABASE_URL environment variable.")
    except Exception as e:
        print(f"WARNING: Database connection failed. Ensure DATABASE_URL is correct in .env. Error: {e}")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_files_path, "index.html"))

@app.get("/health")
async def health_check():
    """Health check endpoint to verify backend is running"""
    return {"status": "ok", "message": "Backend is running"}

@app.get("/api-status")
async def api_status():
    """Check API key and model availability"""
    from llm import test_api_connection, list_available_models
    api_key_set = bool(os.getenv("GOOGLE_API_KEY"))
    is_valid, message = test_api_connection()
    available_models = list_available_models()
    
    return {
        "api_key_set": api_key_set,
        "api_key_valid": is_valid,
        "message": message,
        "available_models": available_models[:10] if available_models else "Could not list models"
    }

@app.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest, db: Any = Depends(get_db)):
    # Validate request
    if not request.url or "wikipedia.org" not in request.url:
        raise HTTPException(status_code=400, detail="A valid Wikipedia URL must be provided")

    target_url = request.url

    # Removed caching check to ensure fresh questions every time as requested
    # if Session and db:
    #     if SQL_AVAILABLE and isinstance(db, Session):
    #         existing_quiz = db.query(Quiz).filter(Quiz.url == target_url).first()
    #         if existing_quiz:
    #             return QuizResponse.from_orm(existing_quiz)

    try:
        # Scrape the Wikipedia page
        scraped_data = scrape_wikipedia(target_url)

        # Generate quiz using LLM
        quiz_data = generate_quiz_data(scraped_data)

        # Create quiz response - ensure title and summary are at top level for consistency
        quiz_response = QuizResponse(
            id=None,  # No ID since not saved to DB
            url=target_url,
            title=quiz_data.get("title") or scraped_data.get("title"),
            summary=quiz_data.get("summary") or scraped_data.get("summary"),
            data=quiz_data,
            created_at=datetime.now()
        )

        # Save to database if available
        if Session and db and SQL_AVAILABLE:
            if isinstance(db, Session):
                new_quiz = Quiz(
                    url=target_url,
                    title=scraped_data.get("title"),
                    summary=scraped_data.get("summary"),
                    data=quiz_data
                )
                db.add(new_quiz)
                db.commit()
                db.refresh(new_quiz)
                quiz_response = QuizResponse.from_orm(new_quiz)

        return quiz_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")

@app.get("/quizzes", response_model=list[QuizResponse])
async def get_quizzes(db: Any = Depends(get_db)):
    if not (Session and db and isinstance(db, Session)):
        return []
    quizzes = db.query(Quiz).all()
    return [QuizResponse.from_orm(quiz) for quiz in quizzes]

@app.get("/quiz/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: int, db: Any = Depends(get_db)):
    if not (Session and db and isinstance(db, Session)):
        raise HTTPException(status_code=404, detail="Database not configured")
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return QuizResponse.from_orm(quiz)

@app.delete("/quiz/{quiz_id}")
async def delete_quiz(quiz_id: int, db: Any = Depends(get_db)):
    if not (Session and db and isinstance(db, Session)):
         raise HTTPException(status_code=503, detail="Database not configured")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    db.delete(quiz)
    db.commit()
    return {"message": "Quiz deleted successfully"}

@app.put("/quiz/{quiz_id}/save-results")
async def save_quiz_results(quiz_id: int, request: SaveResultsRequest, db: Any = Depends(get_db)):
    if not (Session and db and isinstance(db, Session)):
         raise HTTPException(status_code=503, detail="Database not configured")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Update user answers
    quiz.user_answers = request.user_answers
    db.commit()
    
    return {"message": "Quiz results saved successfully"}
