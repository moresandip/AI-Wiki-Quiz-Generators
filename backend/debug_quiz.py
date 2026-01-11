
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from schemas import QuizRequest
from scraper import search_wikipedia, scrape_wikipedia
from llm import generate_quiz_data

load_dotenv()

def test_generation():
    print("--- Starting Debug Test ---")
    
    # 1. Test Topic Search
    topic = "SpaceX"
    print(f"\n1. Testing search for topic: {topic}")
    try:
        url = search_wikipedia(topic)
        print(f"   Found URL: {url}")
    except Exception as e:
        print(f"   FAIL: Search failed: {e}")
        return

    # 2. Test Scraping
    print(f"\n2. Testing scraping for URL: {url}")
    try:
        scraped_data = scrape_wikipedia(url)
        print(f"   Scraped Title: {scraped_data.get('title')}")
        print(f"   Text Length: {len(scraped_data.get('full_text', ''))}")
    except Exception as e:
        print(f"   FAIL: Scraping failed: {e}")
        return

    # 3. Test LLM Generation
    print(f"\n3. Testing LLM Generation (Context limit: 10000)")
    try:
        quiz = generate_quiz_data(scraped_data)
        print("   SUCCESS! Quiz generated.")
        print(f"   Questions generated: {len(quiz.get('quiz', []))}")
    except Exception as e:
        print(f"   FAIL: LLM Generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()
