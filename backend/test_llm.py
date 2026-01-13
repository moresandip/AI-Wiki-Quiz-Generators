import sys
import os
import json
from llm import generate_quiz_data

# Mock scraped data
scraped_data = {
    "title": "Alan Turing",
    "summary": "Alan Mathison Turing OBE FRS (23 June 1912 - 7 June 1954) was an English mathematician, computer scientist, logician, cryptanalyst, philosopher, and theoretical biologist.",
    "sections": ["Early life and education", "Career and research", "Personal life"],
    "key_entities": {
        "people": ["Alan Turing"],
        "organizations": ["University of Cambridge"],
        "locations": ["London"]
    },
    "full_text": "Alan Mathison Turing OBE FRS (23 June 1912 - 7 June 1954) was an English mathematician, computer scientist, logician, cryptanalyst, philosopher, and theoretical biologist. Turing was highly influential in the development of theoretical computer science, providing a formalisation of the concepts of algorithm and computation with the Turing machine, which can be considered a model of a general-purpose computer. Turing is widely considered to be the father of theoretical computer science and artificial intelligence."
}

print("Testing generate_quiz_data...")
try:
    result = generate_quiz_data(scraped_data)
    print("\nGeneration Successful!")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"\nGeneration Failed: {e}")
