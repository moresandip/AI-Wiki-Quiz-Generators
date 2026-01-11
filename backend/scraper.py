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

            # Extract content from introduction and first few sections only for speed
            content_text = ""
            
            # 1. Get introduction (paragraphs before first h2)
            intro_div = soup.find('div', {'id': 'mw-content-text'})
            if intro_div:
                parser_output = intro_div.find('div', {'class': 'mw-parser-output'})
                if parser_output:
                    # Get direct paragraphs until first h2
                    for element in parser_output.children:
                        if element.name == 'h2':
                            break
                        if element.name == 'p':
                            content_text += element.get_text(strip=True) + "\n\n"
                    
                    # 2. Get next 2 main sections
                    sections_count = 0
                    current_section = ""
                    for element in parser_output.find_all(['h2', 'p', 'h3']):
                        if element.name == 'h2':
                            sections_count += 1
                            if sections_count > 3: # Limit to Intro + 3 sections
                                break
                            current_section = element.get_text(strip=True)
                            content_text += f"\n## {current_section}\n"
                        elif element.name in ['p', 'h3']:
                            content_text += element.get_text(strip=True) + "\n"

            # Fallback if sophisticated parsing fails
            if not content_text:
                content_text = soup.get_text()[:6000]

            text = content_text
            
            # Simple Key Entities (from limited text now)
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

def search_wikipedia(topic: str) -> str:
    """
    Search Wikipedia for a topic and return the URL of the top result.
    """
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": topic,
            "limit": 1,
            "namespace": 0,
            "format": "json"
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # data format: [search_term, [titles], [descriptions], [urls]]
        if data and len(data) > 3 and data[3]:
            return data[3][0]
        
        raise ValueError(f"No Wikipedia article found for topic: {topic}")
        
    except Exception as e:
        raise ValueError(f"Failed to search for topic '{topic}': {str(e)}")
