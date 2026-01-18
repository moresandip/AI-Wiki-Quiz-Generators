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
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def log_to_file(message):
    try:
        with open("debug_log.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Failed to write to log: {e}")

app = FastAPI(title="AI Wiki Quiz Generator", version="1.0.0")

# Startup event to create database tables
@app.on_event("startup")
async def startup_event():
    if SQL_AVAILABLE and engine:
        try:
            from models import Base
            # Create tables if they don't exist
            Base.metadata.create_all(bind=engine)
            log_to_file("Database tables created successfully.")
            print("Database tables created successfully.")
        except Exception as e:
            log_to_file(f"Error creating database tables: {e}")
            print(f"Error creating database tables: {e}")


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
        log_to_file(f"Received quiz generation request for URL: {target_url}")
        
        # Scrape the Wikipedia page
        log_to_file("Starting scrape...")
        scraped_data = scrape_wikipedia(target_url)
        log_to_file(f"Scrape successful. Title: {scraped_data.get('title')}")

        # Generate quiz using LLM
        log_to_file("Starting LLM generation...")
        quiz_data = generate_quiz_data(scraped_data)
        log_to_file("LLM generation successful.")

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
                # Check for existing quiz
                existing_quiz = db.query(Quiz).filter(Quiz.url == target_url).first()
                
                if existing_quiz:
                    log_to_file(f"Updating existing quiz for URL: {target_url}")
                    existing_quiz.title = scraped_data.get("title")
                    existing_quiz.summary = scraped_data.get("summary")
                    existing_quiz.data = quiz_data
                    existing_quiz.created_at = datetime.now()
                    # Reset user answers on regeneration
                    existing_quiz.user_answers = {} 
                    
                    db.commit()
                    db.refresh(existing_quiz)
                    quiz_response = QuizResponse.from_orm(existing_quiz)
                    log_to_file(f"Updated quiz ID: {existing_quiz.id}")
                else:
                    log_to_file(f"Creating new quiz for URL: {target_url}")
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
                    log_to_file(f"Saved quiz to DB with ID: {new_quiz.id}")

        return quiz_response
    except Exception as e:
        error_msg = f"Error generating quiz: {str(e)}\n{traceback.format_exc()}"
        log_to_file(error_msg)
        print(error_msg)
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

if __name__ == "__main__":
    try:
        with open("backend_startup_status.txt", "w") as f:
            f.write("Starting backend...\n")
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        with open("backend_startup_status.txt", "a") as f:
            f.write(f"Failed to start: {e}\n")


