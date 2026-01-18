import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

print("--- DIAGNOSIS START ---")

if not api_key:
    print("ERROR: GOOGLE_API_KEY is not set in environment.")
else:
    print(f"API Key found: {api_key[:5]}...{api_key[-4:]}")
    if not api_key.startswith("sk-or-v1"):
        print("WARNING: Key does not look like a standard OpenRouter key (usually starts with sk-or-v1).")

    print("Testing connection to OpenRouter...")
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Diagnosis Script"
        }
        data = {
            "model": "google/gemini-2.0-flash-001",
            "messages": [{"role": "user", "content": "Say 'Connection Successful'"}],
            "max_tokens": 10
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", response.json()['choices'][0]['message']['content'])
            print("SUCCESS: API connection works.")
        else:
            print("FAILURE: API returned error.")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"EXCEPTION: Connection failed - {str(e)}")

print("--- DIAGNOSIS END ---")
