
import time
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import search_wikipedia, scrape_wikipedia
from llm import generate_quiz_data

load_dotenv()

def test_speed():
    print("--- Starting Speed Test ---")
    start_total = time.time()

    # 1. Search
    print("1. Searching for 'Python (programming language)'...")
    start_search = time.time()
    try:
        url = search_wikipedia("Python (programming language)")
        print(f"   Found URL: {url} (took {time.time() - start_search:.2f}s)")
    except Exception as e:
        print(f"   FAIL: Search failed: {e}")
        return

    # 2. Scrape
    print(f"2. Scraping {url}...")
    start_scrape = time.time()
    try:
        scraped_data = scrape_wikipedia(url)
        print(f"   Scraped {len(scraped_data['full_text'])} chars (took {time.time() - start_scrape:.2f}s)")
    except Exception as e:
        print(f"   FAIL: Scraping failed: {e}")
        return

    # 3. Gen AI
    print("3. Generating Quiz (LLM)...")
    start_llm = time.time()
    try:
        quiz = generate_quiz_data(scraped_data)
        print(f"   Generated {len(quiz['quiz'])} questions (took {time.time() - start_llm:.2f}s)")
    except Exception as e:
        print(f"   FAIL: LLM failed: {e}")

    print(f"--- Total Time: {time.time() - start_total:.2f}s ---")

if __name__ == "__main__":
    test_speed()
