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
    """List available models using REST API to keep size small"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return []
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Filter for generating content
            return [m['name'].split('/')[-1] for m in data.get('models', []) 
                    if 'generateContent' in m.get('supportedGenerationMethods', [])]
        return []
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

def test_api_connection():
    """Test if API key is valid using REST API"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return False, "GOOGLE_API_KEY not set in environment"
        
        # Try to list models as a lightweight check
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return True, "API key appears valid"
        else:
            return False, f"API check failed with status {response.status_code}: {response.text}"
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
4. The 'answer' field MUST BE AN EXACT STRING MATCH to one of the options.
5. Provide a short, clear explanation for why the answer is correct, citing the context if possible.
6. Vary the difficulty (easy, medium, hard).

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
    Generate quiz data using direct REST API calls to Google Gemini.
    Replaces the heavy SDK dependency to reduce build size.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
         # Fallback to sample if no key (dev mode) or raise error
         # if SAMPLE_QUIZ_DATA:
         #    return {
         #        "title": scraped_data["title"],
         #        "summary": scraped_data["summary"],
         #        "key_entities": scraped_data["key_entities"],
         #        "sections": scraped_data["sections"],
         #        "quiz": SAMPLE_QUIZ_DATA["quiz"],
         #        "related_topics": SAMPLE_QUIZ_DATA.get("related_topics", [])
         #    }
         raise ValueError("GOOGLE_API_KEY environment variable is not set")

    # ... (previous code) ...

    # Try to generate quiz with models
    try:
        # Hardcoded list of stable models
        models_to_try = [
            "gemini-2.0-flash",
            "gemini-1.5-flash"
        ]
        log_to_file(f"Using hardcoded stable models: {models_to_try}")
        
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

        request_body = {
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": {
                "temperature": 0.9,
                "response_mime_type": "application/json"
            }
        }

        content = ""
        
        for model_name in models_to_try:
            try:
                print(f"Attempting with model: {model_name}")
                url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}"
                
                response = requests.post(url, json=request_body, timeout=60)
                
                if response.status_code == 403:
                    raise ValueError(f"API Key Error (403): {response.text}")

                if response.status_code != 200:
                    if response.status_code == 400 and "response_mime_type" in response.text:
                         del request_body["generationConfig"]["response_mime_type"]
                         response = requests.post(url, json=request_body, timeout=60)
                
                if response.status_code != 200:
                    raise Exception(f"API Error {response.status_code}: {response.text}")

                result = response.json()
                try:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    break
                except (KeyError, IndexError) as e:
                    raise Exception(f"Unexpected response format: {str(e)}")

            except ValueError as ve:
                raise ve # Critical error, stop trying models
            except Exception as e:
                last_error = e
                log_to_file(f"Model {model_name} failed: {str(e)}")
                continue

        if not content:
            raise ValueError(f"All models failed. Last error: {last_error}")

        # Clean up content
        content = content.replace("```json", "").replace("```", "").strip()

        # Parse JSON
        try:
            quiz_data = json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                quiz_data = json.loads(json_match.group())
            else:
                raise ValueError("Failed to parse JSON")

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
            # Return sample data but with the scraped title so it looks somewhat real
            return {
                "title": f"{scraped_data['title']} (DEMO MODE)",
                "summary": "API Key failed. Showing DEMO content. Please update your API key for real quizzes.",
                "key_entities": scraped_data["key_entities"],
                "sections": scraped_data["sections"],
                "quiz": SAMPLE_QUIZ_DATA["quiz"]
            }
        else:
            raise e
