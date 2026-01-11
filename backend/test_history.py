
import requests
import json
import sys
import os

# Base URL - assuming default port
BASE_URL = "http://localhost:8000"

def test_history_flow():
    print("--- Testing History & Delete Flow ---")

    # 1. Generate a Quiz (should save to history)
    print("\n1. Generating Quiz for 'Test Topic'...")
    try:
        payload = {"topic": "Unit Testing"}
        response = requests.post(f"{BASE_URL}/generate-quiz", json=payload)
        if response.status_code == 200:
            quiz_data = response.json()
            quiz_id = quiz_data.get("id") # Note: API might not return ID in generate response, need to check main.py
            print("   Success! Quiz generated.")
        else:
            print(f"   FAIL: Generation failed ({response.status_code}): {response.text}")
            return
    except Exception as e:
        print(f"   FAIL: Connection error: {e}")
        return

    # 2. Check History
    print("\n2. Checking History...")
    try:
        response = requests.get(f"{BASE_URL}/quizzes")
        if response.status_code == 200:
            history = response.json()
            print(f"   History count: {len(history)}")
            
            # Find the quiz we just created
            # Note: Since ID might not be in generate response, we look for the last one or by title
            latest_quiz = history[-1] if history else None
            
            if latest_quiz:
                print(f"   Latest Quiz ID: {latest_quiz.get('id')}")
                print(f"   Latest Quiz Title: {latest_quiz.get('title')}")
                quiz_id = latest_quiz.get('id')
            else:
                print("   FAIL: History is empty!")
                return
        else:
            print(f"   FAIL: Could not fetch history ({response.status_code})")
            return
    except Exception as e:
        print(f"   FAIL: Connection error: {e}")
        return

    # 3. Delete Quiz
    if quiz_id:
        print(f"\n3. Deleting Quiz ID {quiz_id}...")
        try:
            response = requests.delete(f"{BASE_URL}/quiz/{quiz_id}")
            if response.status_code == 200:
                print("   Success! Quiz deleted.")
            else:
                print(f"   FAIL: Delete failed ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"   FAIL: Connection error: {e}")

    # 4. Verify Deletion
    print("\n4. Verifying Deletion...")
    try:
        response = requests.get(f"{BASE_URL}/quizzes")
        history = response.json()
        ids = [q['id'] for q in history]
        if quiz_id not in ids:
             print("   Success! Quiz no longer in history.")
        else:
             print("   FAIL: Quiz still exists in history!")
    except Exception as e:
        print(f"   FAIL: Connection error: {e}")

if __name__ == "__main__":
    test_history_flow()
