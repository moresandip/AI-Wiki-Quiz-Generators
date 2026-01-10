import requests
from bs4 import BeautifulSoup
import re
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    """Create a requests session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # Total number of retries
        backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry
        allowed_methods=["GET"]  # Only retry GET requests
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def scrape_wikipedia(url: str) -> dict:
    """
    Scrape a Wikipedia article and extract title, summary, sections, and key entities.
    Includes retry logic and better error handling for network issues.
    """
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Create session with retry strategy
            session = create_session_with_retries()
            
            # Make request with timeout
            response = session.get(
                url, 
                headers=headers,
                timeout=(10, 30)  # (connect timeout, read timeout) in seconds
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.find('h1', {'id': 'firstHeading'}).get_text(strip=True) if soup.find('h1', {'id': 'firstHeading'}) else "Unknown Title"

            # Extract summary (first paragraph)
            summary_paragraph = soup.find('p', class_=lambda x: x != 'mw-empty-elt')
            summary = summary_paragraph.get_text(strip=True) if summary_paragraph else ""

            # Extract sections (headings)
            sections = []
            for heading in soup.find_all(['h2', 'h3'], {'class': 'mw-headline'}):
                sections.append(heading.get_text(strip=True))

            # Extract key entities (simple regex-based extraction)
            text = soup.get_text()
            people = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text)  # Simple name pattern
            organizations = re.findall(r'\b[A-Z][a-z]+ (University|College|Institute|Company|Corporation|Foundation)\b', text)
            locations = re.findall(r'\b[A-Z][a-z]+, [A-Z][a-z]+\b', text)  # City, Country

            # Remove duplicates and limit
            people = list(set(people))[:10]
            organizations = list(set(organizations))[:10]
            locations = list(set(locations))[:10]

            result = {
                "title": title,
                "summary": summary,
                "sections": sections,
                "key_entities": {
                    "people": people,
                    "organizations": organizations,
                    "locations": locations
                },
                "full_text": text  # For LLM processing
            }
            
            # Close session
            session.close()
            return result
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            raise ValueError(
                f"Connection timeout while scraping {url}. "
                "Please check your internet connection and try again."
            )
        except requests.exceptions.ConnectionError as e:
            error_msg = str(e).lower()
            if "name resolution" in error_msg or "getaddrinfo failed" in error_msg or "failed to resolve" in error_msg:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise ValueError(
                    f"Network connection error: Cannot resolve Wikipedia domain.\n"
                    "Possible causes:\n"
                    "1. No internet connection\n"
                    "2. DNS server issues\n"
                    "3. Firewall blocking access\n"
                    "4. VPN or proxy issues\n\n"
                    "Please check your internet connection and try again."
                )
            else:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise ValueError(
                    f"Connection error while scraping {url}: {str(e)}\n"
                    "Please check your internet connection and try again."
                )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Wikipedia page not found: {url}\nPlease check the URL and try again.")
            elif e.response.status_code == 403:
                raise ValueError(f"Access forbidden: {url}\nWikipedia may be blocking the request.")
            else:
                raise ValueError(f"HTTP error {e.response.status_code} while scraping {url}: {str(e)}")
        except Exception as e:
            error_msg = str(e).lower()
            if "name resolution" in error_msg or "getaddrinfo failed" in error_msg or "failed to resolve" in error_msg:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise ValueError(
                    f"Network error: Cannot connect to Wikipedia.\n"
                    "Please check your internet connection and DNS settings.\n"
                    f"Original error: {str(e)}"
                )
            else:
                raise ValueError(f"Failed to scrape {url}: {str(e)}")
    
    # If we get here, all retries failed
    raise ValueError(f"Failed to scrape {url} after {max_retries} attempts. Please check your internet connection.")
