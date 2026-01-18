import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("API Key not found in .env")
    exit(1)

print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, can you hear me?")
    print("API Test Successful!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"API Test Failed: {e}")
