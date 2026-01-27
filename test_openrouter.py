#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter_connection():
    """Test OpenRouter API connection"""
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        return False

    print(f"🔑 API Key found: {api_key[:10]}...")

    # Test 1: Check API key validity
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )

        if response.status_code == 200:
            print("✅ OpenRouter API key is valid")
        else:
            print(f"❌ OpenRouter API key invalid: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False

    # Test 2: Try a simple generation
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AI Wiki Quiz Generator",
        }

        data = {
            "model": "google/gemini-2.0-flash-lite-preview-02-05:free",
            "messages": [
                {"role": "user", "content": "Say 'Hello, OpenRouter API is working!'"}
            ],
            "temperature": 0.7,
            "max_tokens": 50
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ API call successful: {content.strip()}")
            return True
        else:
            print(f"❌ API call failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error during API call: {e}")
        return False

if __name__ == "__main__":
    print("Testing OpenRouter API connection...")
    success = test_openrouter_connection()
    if success:
        print("\n🎉 OpenRouter API is working correctly!")
    else:
        print("\n💥 OpenRouter API test failed!")
