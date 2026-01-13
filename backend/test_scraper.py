from scraper import scrape_wikipedia
import json

def test_scraper():
    url = "https://en.wikipedia.org/wiki/Alan_Turing"
    print(f"Testing scraper with URL: {url}")
    try:
        data = scrape_wikipedia(url)
        print("\nScraping Successful!")
        print(f"Title: {data['title']}")
        print(f"Summary: {data['summary'][:100].encode('utf-8', errors='ignore').decode('utf-8')}...")
        print(f"Sections found: {len(data['sections'])}")
        print(f"Entities found: {len(data['key_entities']['people'])} people")
        
        # Save sample data
        with open("../sample_data/scraped_sample.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            print("\nSaved scraped data to sample_data/scraped_sample.json")
            
    except Exception as e:
        print(f"\nScraping Failed: {str(e)}")

if __name__ == "__main__":
    test_scraper()
