
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENROUTER_API_KEY")
if key:
    print(f"OPENROUTER_API_KEY found: {key[:5]}...{key[-5:]}")
else:
    print("OPENROUTER_API_KEY NOT found")

google_key = os.getenv("GOOGLE_API_KEY")
if google_key:
     print(f"GOOGLE_API_KEY found: {google_key[:5]}...")
else:
    print("GOOGLE_API_KEY NOT found (Correct)")
