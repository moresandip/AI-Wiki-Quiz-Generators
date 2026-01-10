import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment.")
    exit(1)

print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")

try:
    genai.configure(api_key=api_key)
    print("Listing available models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

print("\nTrying to generate content with 'gemini-pro'...")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, can you hear me?")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Error generating content with gemini-pro: {e}")

print("\nTrying to generate content with 'gemini-1.5-flash'...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, can you hear me?")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Error generating content with gemini-1.5-flash: {e}")
