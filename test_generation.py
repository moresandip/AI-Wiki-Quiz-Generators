import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.llm import generate_quiz_data
except ImportError:
    print("Could not import backend.llm. Making sure path is correct.")
    sys.path.append('backend')
    from llm import generate_quiz_data

# Mock scraped data
mock_scraped_data = {
    "title": "Test Article: Artificial Intelligence",
    "summary": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans.",
    "sections": ["History", "Goals", "Tools"],
    "key_entities": ["Turing test", "Deep learning"],
    "full_text": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals."
}

print(f"Checking API Key: {os.getenv('GOOGLE_API_KEY')[:10]}...")

try:
    print("Attempting to generate quiz...")
    result = generate_quiz_data(mock_scraped_data)
    print("\nGeneration Result:")
    print(f"Title: {result.get('title')}")
    print(f"Quiz Questions: {len(result.get('quiz', []))}")
    if len(result.get('quiz', [])) > 0:
        print(f"First Question: {result['quiz'][0]['question']}")
    else:
        print("No questions generated.")
except Exception as e:
    print(f"\nFAILED: {e}")
