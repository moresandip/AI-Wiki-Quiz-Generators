import os
from dotenv import load_dotenv
import google.generativeai as genai

print("--- DIAGNOSTIC START ---")
try:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"API Key present: {bool(api_key)}")
    
    if api_key:
        print(f"API Key first 4 chars: {api_key[:4]}...")
        try:
            genai.configure(api_key=api_key)
            # Try a simple model first
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("Attempting to generate content...")
            response = model.generate_content("Test")
            print("GenAI Test: Success")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"GenAI Test: Failed - {e}")
    else:
        print("ERROR: GOOGLE_API_KEY not found in environment variables.")
        print("Please ensure backend/.env exists and contains GOOGLE_API_KEY=...")
except Exception as e:
    print(f"Diagnostic Script Error: {e}")
print("--- DIAGNOSTIC END ---")
