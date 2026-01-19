import os
import re
import json
import requests
from dotenv import load_dotenv
import datetime

def log_to_file(message):
    try:
        with open("debug_log.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] [LLM] {message}\n")
    except Exception:
        pass

# Load sample data as fallback
SAMPLE_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'sample_data', 'sample_output.json')
try:
    with open(SAMPLE_DATA_PATH, 'r') as f:
        SAMPLE_QUIZ_DATA = json.load(f)
except Exception as e:
    SAMPLE_QUIZ_DATA = None
    print(f"Warning: Could not load sample data: {e}")

# Load environment variables from .env file
load_dotenv()

def list_available_models():
    """List available models based on configured API key"""
    google_key = os.getenv("GOOGLE_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    models = []
    if google_key:
        models.extend(["gemini-1.5-flash", "gemini-1.5-pro"])
    if openrouter_key:
        models.extend(["google/gemini-2.0-flash-lite-preview-02-05:free", "google/gemini-2.0-pro-exp-02-05:free", "deepseek/deepseek-r1:free"])
        
    return models

def test_api_connection():
    """Test if a valid API key is present"""
    google_key = os.getenv("GOOGLE_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not google_key and not openrouter_key:
        return False, "No API key found (GOOGLE_API_KEY or OPENROUTER_API_KEY)"

    if google_key:
        # Test Google Key
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash?key={google_key}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return True, "Google Gemini API key is valid"
        except Exception as e:
            if not openrouter_key:
                return False, f"Google API test failed: {str(e)}"

    if openrouter_key:
        # Test OpenRouter Key
        try:
            response = requests.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {openrouter_key}"},
                timeout=10
            )
            if response.status_code == 200:
                return True, "OpenRouter API key is valid"
            elif response.status_code == 401:
                return False, "Invalid OpenRouter API key"
        except Exception as e:
            return False, f"OpenRouter API test failed: {str(e)}"
            
    return False, "API test failed"

# Prompt template for quiz generation
QUIZ_PROMPT_TEMPLATE = """
You are an expert quiz generator. Your task is to create a highly accurate multiple-choice quiz based ONLY on the provided Wikipedia article content.

Article Title: {title}
Summary: {summary}
Sections: {sections}
Key Entities: {key_entities}
Full Text: {full_text}

Instructions:
1. Generate 5-10 multiple-choice questions. 
2. **IMPORTANT**: Focus on different aspects of the article than typical generic questions.
3. **STRICT CONSTRAINT**: You must use ONLY the provided text to generate questions and answers. Do not use your internal knowledge base. If a fact is not in the text, do not ask about it.
4. Each question must have 4 options (A, B, C, D).
5. The 'answer' field MUST BE AN EXACT STRING MATCH to one of the options.
6. Provide a short, clear explanation for why the answer is correct, citing the context if possible.
7. Vary the difficulty (easy, medium, hard).

Output the result in this exact JSON format:
{{
  "quiz": [
    {{
      "question": "Question text",
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "answer": "Option 2",
      "difficulty": "easy",
      "explanation": "Explanation here."
    }}
  ]
}}

Output strictly valid JSON only.
"""

def generate_with_openrouter(api_key, prompt_text):
    """Generate content using OpenRouter API"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000", # Optional, for including your app on openrouter.ai rankings.
        "X-Title": "AI Wiki Quiz Generator", # Optional. Shows in rankings on openrouter.ai.
    }
    
    # List of models to try in order of preference
    models = [
        "google/gemini-2.0-flash-lite-preview-02-05:free",
        "google/gemini-2.0-pro-exp-02-05:free",
        "deepseek/deepseek-r1:free"
    ]
    
    last_error = None
    
    for model in models:
        try:
            log_to_file(f"Attempting OpenRouter with model: {model}")
            data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt_text}
                ],
                "temperature": 0.7,
                "top_p": 0.9,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"OpenRouter Error {response.status_code}: {response.text}"
                log_to_file(error_msg)
                raise Exception(error_msg)
                
            result = response.json()
            content = result['choices'][0]['message']['content']
            return content
            
        except Exception as e:
            last_error = e
            log_to_file(f"OpenRouter model {model} failed: {str(e)}")
            continue
            
    raise Exception(f"All OpenRouter models failed. Last error: {last_error}")

def generate_with_gemini(api_key, prompt_text):
    """Generate content using Google Gemini API"""
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    last_error = None
    
    for model_name in models_to_try:
        try:
            log_to_file(f"Attempting Gemini with model: {model_name}")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{"parts": [{"text": prompt_text}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"API Error {response.status_code}: {response.text}")
                
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
            
        except Exception as e:
            last_error = e
            log_to_file(f"Gemini model {model_name} failed: {str(e)}")
            continue
            
    raise Exception(f"All Gemini models failed. Last error: {last_error}")

def generate_quiz_data(scraped_data):
    """
    Generate quiz data using configured API (OpenRouter or Gemini).
    """
    google_key = os.getenv("GOOGLE_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not google_key and not openrouter_key:
         log_to_file("CRITICAL ERROR: No API key set. Falling back to sample data.")
         raise ValueError("No API key configured (GOOGLE_API_KEY or OPENROUTER_API_KEY)")

    try:
        log_to_file(f"Generating quiz for: {scraped_data.get('title')}")

        # Format the prompt
        prompt_text = QUIZ_PROMPT_TEMPLATE.format(
            title=scraped_data["title"],
            summary=scraped_data["summary"],
            sections=", ".join(scraped_data["sections"]),
            key_entities=json.dumps(scraped_data["key_entities"]),
            full_text=scraped_data["full_text"][:6000]
        )

        content = ""
        
        # Prefer OpenRouter if available (since user explicitly provided it)
        if openrouter_key:
            content = generate_with_openrouter(openrouter_key, prompt_text)
        elif google_key:
            content = generate_with_gemini(google_key, prompt_text)

        # Clean up content
        content = content.strip()
        
        # Parse JSON
        try:
            quiz_data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                quiz_data = json.loads(json_match.group())
            else:
                raise ValueError(f"Failed to parse JSON from response: {content[:200]}...")

        return {
            "title": scraped_data["title"],
            "summary": scraped_data["summary"],
            "key_entities": scraped_data["key_entities"],
            "sections": scraped_data["sections"],
            "quiz": quiz_data.get("quiz", [])
        }

    except Exception as e:
        log_to_file(f"Quiz generation failed: {e}")
        print(f"Quiz generation failed: {e}")

        if SAMPLE_QUIZ_DATA:
            log_to_file("Falling back to SAMPLE DATA (Demo Mode)")
            print("Falling back to SAMPLE DATA (Demo Mode)")
            return {
                "title": scraped_data['title'],
                "summary": scraped_data['summary'],
                "key_entities": scraped_data["key_entities"],
                "sections": scraped_data["sections"],
                "quiz": SAMPLE_QUIZ_DATA["quiz"]
            }
        else:
            raise e
