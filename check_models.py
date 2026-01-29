
import sys
import os
import requests
from dotenv import load_dotenv

# Ensure we load env correctly
DOTENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(DOTENV_PATH)
api_key = os.getenv("GOOGLE_API_KEY")

output_file = "model_list_debug.txt"

with open(output_file, "w") as f:
    if not api_key:
        f.write("No API key found.\n")
        sys.exit(1)
        
    f.write(f"Key found: {api_key[:5]}...\n")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        f.write(f"Status Code: {response.status_code}\n")
        if response.status_code == 200:
            data = response.json()
            f.write("Available Models:\n")
            for m in data.get('models', []):
                f.write(f"- {m['name']}\n")
        else:
            f.write(f"Error: {response.text}\n")
    except Exception as e:
        f.write(f"Exception: {str(e)}\n")
