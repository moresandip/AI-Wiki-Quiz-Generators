
import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
google_key = os.getenv("GOOGLE_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

if not google_key and not openrouter_key:
    print("API Key not found in .env")
    exit(1)

if google_key:
    print(f"Google API Key found: {google_key[:5]}...{google_key[-5:]}")
    try:
        genai.configure(api_key=google_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello")
        print("Google API Test Successful!")
    except Exception as e:
        print(f"Google API Test Failed: {e}")

if openrouter_key:
    # Basic existence check is enough for startup script
    print(f"OpenRouter API Key found: {openrouter_key[:5]}...{openrouter_key[-5:]}")
    print("OpenRouter configured (skip validation)")
