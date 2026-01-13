import requests
import json
import sys
import datetime

BASE_URL = "http://localhost:8000"

def log(msg):
    print(f"[TEST] {msg}")

def test_crud():
    # 1. Seed DB with a dummy quiz
    log("Seeding database with dummy quiz...")
    try:
        from database import SessionLocal, engine, Base
        from models import Quiz
        
        # Ensure tables exist
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        dummy_quiz = Quiz(
            url="http://test-crud.com",
            title="Test CRUD Quiz",
            summary="Test Summary",
            data={"quiz": []},
            created_at=datetime.datetime.now()
        )
        db.add(dummy_quiz)
        db.commit()
        db.refresh(dummy_quiz)
        quiz_id = dummy_quiz.id
        db.close()
        log(f"Seeded quiz with ID: {quiz_id}")
        
    except Exception as e:
        log(f"Failed to seed DB: {e}")
        return

    # 2. Test Save Results
    log(f"Testing Save Results for Quiz ID {quiz_id}...")
    user_answers = {"0": "Option A", "1": "Option B"}
    response = requests.put(
        f"{BASE_URL}/quiz/{quiz_id}/save-results",
        json={"user_answers": user_answers}
    )
    
    if response.status_code == 200:
        log("Save Results: Success")
    else:
        log(f"Save Results: Failed - {response.status_code} {response.text}")

    # 3. Verify Save
    log("Verifying Save...")
    response = requests.get(f"{BASE_URL}/quiz/{quiz_id}")
    if response.status_code == 200:
        data = response.json()
        saved_answers = data.get("user_answers")
        if saved_answers == user_answers:
            log("Verification: Success (Answers match)")
        else:
            log(f"Verification: Failed. Expected {user_answers}, got {saved_answers}")
    else:
        log(f"Verification: Failed to fetch quiz - {response.status_code}")

    # 4. Test Delete
    log(f"Testing Delete for Quiz ID {quiz_id}...")
    response = requests.delete(f"{BASE_URL}/quiz/{quiz_id}")
    
    if response.status_code == 200:
        log("Delete: Success")
    else:
        log(f"Delete: Failed - {response.status_code} {response.text}")

    # 5. Verify Delete
    log("Verifying Delete...")
    response = requests.get(f"{BASE_URL}/quiz/{quiz_id}")
    if response.status_code == 404:
        log("Verification: Success (Quiz not found)")
    else:
        log(f"Verification: Failed. Expected 404, got {response.status_code}")

if __name__ == "__main__":
    try:
        test_crud()
    except Exception as e:
        log(f"Exception: {e}")
