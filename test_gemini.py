#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_connection():
    """Test Google Gemini API connection"""
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        return False

    print(f"🔑 API Key found: {api_key[:10]}...")

    # Test 1: Check API key validity by listing models
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            print("✅ Google Gemini API key is valid")
        else:
            print(f"❌ Google Gemini API key invalid: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False

    # Test 2: Try a simple generation with the latest model
    try:
        models_to_try = ["gemini-1.5-flash-latest", "gemini-1.5-flash"]

        for model in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                data = {
                    "contents": [{"parts": [{"text": "Say 'Hello, Google Gemini API is working!'"}]}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 100,
                    }
                }

                response = requests.post(url, headers=headers, json=data, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ API call successful with {model}: {content.strip()}")
                    return True
                else:
                    print(f"⚠️  {model} failed: {response.status_code} - trying next model")
                    continue

            except Exception as e:
                print(f"⚠️  {model} error: {e} - trying next model")
                continue

        print("❌ All Gemini models failed")
        return False

    except Exception as e:
        print(f"❌ Error during API call: {e}")
        return False

if __name__ == "__main__":
    print("Testing Google Gemini API connection...")
    success = test_gemini_connection()
    if success:
        print("\n🎉 Google Gemini API is working correctly!")
    else:
        print("\n💥 Google Gemini API test failed!")
