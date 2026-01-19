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
    """List available models using Google Gemini API"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return []

    # Google Gemini models
    return ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest", "gemini-pro"]

def test_api_connection():
    """Test if Google API key is valid"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return False, "GOOGLE_API_KEY not set in environment"

        # Check if it looks like a Google API key
        if not api_key.startswith("AIza"):
            return False, "API key should start with 'AIza' for Google Gemini"

        # Simple test request to check if key is valid
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash?key={api_key}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return True, "Google Gemini API key is valid"
        elif response.status_code == 400:
            return False, "Invalid API key format"
        elif response.status_code == 403:
            return False, "API key does not have permission or quota exceeded"
        else:
            return False, f"API test failed with status {response.status_code}"

    except requests.exceptions.RequestException as e:
        return False, f"Network error testing API: {str(e)}"
    except Exception as e:
        return False, f"API connection test failed: {str(e)}"

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

def generate_quiz_data(scraped_data):
    """
    Generate quiz data using Google Gemini API.
    """
    # TODO: Replace this with a secure way of storing the API key, such as environment variables.
    api_key = "AIzaSyAUC5WN8MpqTlYjtmvhXcuQMkxkGwQfrXY"
    if not api_key:
         log_to_file("CRITICAL ERROR: GOOGLE_API_KEY environment variable is not set. Falling back to sample data.")
         raise ValueError("GOOGLE_API_KEY environment variable is not set")

    # Try to generate quiz with Google Gemini models
    try:
        # Google Gemini models to try
        models_to_try = [
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro-latest",
            "gemini-pro"
        ]
        log_to_file(f"Using Google Gemini models: {models_to_try}")

        last_error = None
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

        for model_name in models_to_try:
            try:
                print(f"Attempting with model: {model_name}")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

                headers = {
                    "Content-Type": "application/json"
                }

                data = {
                    "contents": [{
                        "parts": [{
                            "text": prompt_text
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 2048,
                    }
                }

                response = requests.post(url, headers=headers, json=data, timeout=60)

                if response.status_code != 200:
                    error_data = response.json()
                    raise Exception(f"API Error {response.status_code}: {error_data.get('error', {}).get('message', response.text)}")

                result = response.json()
                try:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    break
                except (KeyError, IndexError) as e:
                    raise Exception(f"Unexpected response format: {str(e)}")

            except Exception as e:
                last_error = e
                log_to_file(f"Model {model_name} failed: {str(e)}")
                continue

        if not content:
            raise ValueError(f"All Google Gemini models failed. Last error: {last_error}")

        # Clean up content - Gemini doesn't wrap in code blocks like other APIs
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
                raise ValueError(f"Failed to parse JSON from Gemini response: {content[:200]}...")

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
            log_to_file("Falling back to SAMPLE DATA (Demo Mode) - This usually happens because the API Key is invalid or missing.")
            print("Falling back to SAMPLE DATA (Demo Mode)")
            # Return sample data but with the scraped title/summary so it looks real
            return {
                "title": scraped_data['title'],
                "summary": scraped_data['summary'],
                "key_entities": scraped_data["key_entities"],
                "sections": scraped_data["sections"],
                "quiz": SAMPLE_QUIZ_DATA["quiz"]
            }
        else:
            raise e
