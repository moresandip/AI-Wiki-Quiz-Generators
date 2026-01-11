import os
import re
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

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
    """List available models using google-generativeai library"""
    if not GENAI_AVAILABLE:
        return []
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return []
        genai.configure(api_key=api_key)
        models = genai.list_models()
        return [model.name.split('/')[-1] for model in models if 'generateContent' in model.supported_generation_methods]
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

def test_api_connection():
    """Test if API key is valid by trying to create an LLM instance"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return False, "GOOGLE_API_KEY not set in environment"
        
        # Try to list available models first
        if GENAI_AVAILABLE:
            available = list_available_models()
            if available:
                print(f"Available models: {', '.join(available[:5])}...")  # Show first 5
        
        # Try to create an LLM instance with latest model
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=api_key)
        return True, "API key appears valid"
    except Exception as e:
        return False, f"API connection test failed: {str(e)}"

def get_llm(model_name=None):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    # Try latest model names - these are the most current as of 2024
    # Fallback options will be tried in generate_quiz_data if this fails
    model = model_name or "gemini-2.0-flash-exp"
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.7,
    )

# Prompt template for quiz generation
quiz_prompt_template = """
Based on the following Wikipedia article content, generate a quiz with 5-10 multiple-choice questions. Each question should have 4 options (A-D), one correct answer, a short explanation, and a difficulty level (easy, medium, hard).

Article Title: {title}
Summary: {summary}
Sections: {sections}
Key Entities: {key_entities}
Full Text: {full_text}

Output the quiz in the following JSON format:
{{
  "quiz": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Correct Option Text",
      "difficulty": "easy/medium/hard",
      "explanation": "Short explanation"
    }}
  ],
  "related_topics": ["Topic1", "Topic2", "Topic3"]
}}

Ensure questions are relevant to the article content and vary in difficulty.
"""

quiz_prompt = PromptTemplate(
    input_variables=["title", "summary", "sections", "key_entities", "full_text"],
    template=quiz_prompt_template
)

quiz_chain = None

def get_quiz_chain():
    global quiz_chain
    if quiz_chain is None:
        llm_instance = get_llm()
        quiz_chain = quiz_prompt | llm_instance
    return quiz_chain

def generate_quiz_data(scraped_data):
    """
    Generate quiz data using the LLM based on scraped Wikipedia data.
    Tries multiple models if one fails due to quota or availability issues.
    """
    # List of models to try in order (latest models first)
    # Updated with current model names as of 2024
    models_to_try = [
        "gemini-2.0-flash-exp",           # Latest experimental
        "gemini-2.0-flash-thinking-exp",  # Thinking variant
        "gemini-1.5-flash-latest",        # Latest stable flash
        "gemini-1.5-pro-latest",          # Latest stable pro
        "gemini-1.5-flash",               # Standard flash
        "gemini-1.5-pro",                 # Standard pro
        "gemini-pro"                      # Legacy fallback
    ]
    last_error = None
    tried_models = []
    
    for model_name in models_to_try:
        try:
            # Prepare input for the LLM
            input_data = {
                "title": scraped_data["title"],
                "summary": scraped_data["summary"],
                "sections": ", ".join(scraped_data["sections"]),
                "key_entities": json.dumps(scraped_data["key_entities"]),
                "full_text": scraped_data["full_text"][:10000]  # Limit text length for API
            }

            # Create a new chain with the current model
            llm_instance = get_llm(model_name)
            chain = quiz_prompt | llm_instance
            result = chain.invoke(input_data)
            
            # If we get here, the model worked, break out of the loop
            break
            
        except Exception as e:
            error_msg = str(e)
            last_error = e
            tried_models.append(f"{model_name}: {error_msg[:100]}")
            # If it's a quota/availability/not found issue, try next model
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg or "NOT_FOUND" in error_msg or "404" in error_msg or "not found" in error_msg.lower():
                print(f"Model {model_name} failed ({error_msg[:80]}), trying next model...")
                continue
            else:
                # For other errors, raise immediately
                raise
    
    # If all models failed, fall back to sample data if available
    if last_error:
        if SAMPLE_QUIZ_DATA:
            print("WARNING: All models failed. Falling back to sample data for demonstration.")
            return {
                "title": scraped_data["title"],
                "summary": scraped_data["summary"],
                "key_entities": scraped_data["key_entities"],
                "sections": scraped_data["sections"],
                "quiz": SAMPLE_QUIZ_DATA["quiz"],
                "related_topics": SAMPLE_QUIZ_DATA.get("related_topics", [])
            }
        else:
            # If no sample data, raise the error
            error_msg = str(last_error)
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg or "quota" in error_msg.lower():
                raise ValueError(
                    "API quota exceeded. This usually means:\n"
                    "1. You've reached your daily free tier limit (wait 24 hours)\n"
                    "2. You've made too many requests too quickly (wait a few minutes)\n"
                    "3. Check your quota at: https://ai.dev/rate-limit\n\n"
                    "Please try again later or upgrade your API plan."
                )
            elif "NOT_FOUND" in error_msg or "404" in error_msg or "not found" in error_msg.lower():
                models_tried_str = "\n".join(tried_models) if tried_models else "No models tried"
                raise ValueError(
                    f"None of the available models worked. Tried {len(tried_models)} models.\n\n"
                    "Likely Cause: API not enabled or packages need updating.\n"
                    "Solutions:\n"
                    "1. ENABLE API: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com\n"
                    "2. Update packages: cd backend && venv\\Scripts\\activate && pip install --upgrade langchain-google-genai google-generativeai\n"
                    "3. Verify API Key: https://aistudio.google.com/app/apikey\n"
                    "4. Check status: Visit http://localhost:8000/api-status\n"
                    f"Models tried: {models_tried_str[:200]}..."
                )
            else:
                raise ValueError(f"Failed to generate quiz: {error_msg}")

    # Extract content from the response (LangChain returns a message object)
    if hasattr(result, 'content'):
        content = result.content
    elif isinstance(result, str):
        content = result
    else:
        content = str(result)

    # Clean up the content - remove markdown code blocks if present
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]  # Remove ```json
    elif content.startswith("```"):
        content = content[3:]   # Remove ```
    if content.endswith("```"):
        content = content[:-3]  # Remove closing ```
    content = content.strip()

    # Parse the JSON response
    try:
        quiz_data = json.loads(content)
    except json.JSONDecodeError as e:
        # Try to extract JSON from the response if it's embedded in text
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            quiz_data = json.loads(json_match.group())
        else:
            raise ValueError(f"Failed to parse JSON from LLM response: {str(e)}\nResponse content: {content[:500]}")

    # Add the structured data to match the API output
    return {
        "title": scraped_data["title"],
        "summary": scraped_data["summary"],
        "key_entities": scraped_data["key_entities"],
        "sections": scraped_data["sections"],
        "quiz": quiz_data["quiz"],
        "related_topics": quiz_data["related_topics"]
    }
