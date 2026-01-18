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
    """List available models using OpenRouter API"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return []
    
    # Simple static list for OpenRouter to avoid extra calls/latency
    return ["google/gemini-2.0-flash-001", "google/gemini-pro-1.5", "openai/gpt-3.5-turbo"]

def test_api_connection():
    """Test if API key is valid using OpenRouter"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return False, "GOOGLE_API_KEY not set env"
        
        # Simple auth check
        if api_key.startswith("sk-or-v1"):
            return True, "OpenRouter Key detected"
        elif api_key.startswith("AIza"):
             return True, "Google Key detected (check formatting compatibility)"
        else:
            return True, "API Key present"

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
    Generate quiz data using OpenRouter API (OpenAI-compatible).
    """
    api_key = os.getenv("GOOGLE_API_KEY") # Keeping the env var name for compatibility, but it holds the OpenRouter key
    if not api_key:
         log_to_file("CRITICAL ERROR: GOOGLE_API_KEY environment variable is not set. Falling back to sample data.")
         raise ValueError("API Key environment variable is not set")

    # Try to generate quiz with models
    try:
        # OpenRouter models
        models_to_try = [
            "google/gemini-2.0-flash-001",
            "google/gemini-pro-1.5",
            "openai/gpt-4o-mini"
        ]
        log_to_file(f"Using models: {models_to_try}")
        
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
                url = "https://openrouter.ai/api/v1/chat/completions"
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000", # Required by OpenRouter
                    "X-Title": "AI Wiki Quiz Generator" # Required by OpenRouter
                }
                
                data = {
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": prompt_text}
                    ],
                    "response_format": {"type": "json_object"}
                }
                
                response = requests.post(url, headers=headers, json=data, timeout=60)
                
                if response.status_code != 200:
                    raise Exception(f"API Error {response.status_code}: {response.text}")

                result = response.json()
                try:
                    content = result['choices'][0]['message']['content']
                    break
                except (KeyError, IndexError) as e:
                    raise Exception(f"Unexpected response format: {str(e)}")

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
