import os
import requests
from dotenv import load_dotenv

def log(msg):
    with open("api_test_result.txt", "a") as f:
        f.write(msg + "\n")

# Clear file
with open("api_test_result.txt", "w") as f:
    f.write("Starting API Test\n")

try:
    load_dotenv()
    log("Loaded dotenv")
except Exception as e:
    log(f"Error loading dotenv: {e}")

api_key = os.getenv("GOOGLE_API_KEY")
log(f"API Key present: {bool(api_key)}")

if api_key:
    # Mask key for security in logs
    log(f"API Key: {api_key[:5]}...{api_key[-5:]}")
    
    # List models
    try:
        log("Listing available models...")
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(list_url, timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models if 'generateContent' in m.get('supportedGenerationMethods', [])]
            log(f"Available Models: {model_names}")
            
            # Try generation with the first available model
            if model_names:
                target_model = model_names[0].split('/')[-1] # remove models/ prefix
                log(f"Testing generation with: {target_model}")
                
                gen_url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={api_key}"
                data = {
                    "contents": [{
                        "parts": [{"text": "Explain quantum computing in one sentence."}]
                    }]
                }
                response = requests.post(gen_url, json=data, timeout=10)
                log(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    log(f"Response: {response.json()['candidates'][0]['content']['parts'][0]['text']}")
                    log("API Test: SUCCESS")
                else:
                    log(f"Response: {response.text}")
                    log("API Test: FAILED")
        else:
            log(f"Failed to list models: {response.status_code} {response.text}")
    except Exception as e:
        log(f"Error listing models: {e}")
else:
    log("API Test: SKIPPED (No Key)")
