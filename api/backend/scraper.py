import requests
from bs4 import BeautifulSoup
import re

def scrape_wikipedia(url):
    """
    Scrape content from a Wikipedia page.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Get title
        title = soup.find('h1', {'id': 'firstHeading'})
        title = title.text.strip() if title else "Unknown Title"

        # Get main content
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if content_div:
            # Remove unwanted elements
            for element in content_div.find_all(['table', 'div', {'class': 'reflist'}, {'class': 'navbox'}]):
                element.decompose()

            # Get text from paragraphs
            paragraphs = content_div.find_all('p')
            content = ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])

            # Clean up the content
            content = re.sub(r'\[.*?\]', '', content)  # Remove references
            content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
            content = content[:10000]  # Limit content length
        else:
            content = "Content not found"

        return {
            'title': title,
            'content': content,
            'url': url
        }

    except Exception as e:
        raise ValueError(f"Failed to scrape Wikipedia page: {str(e)}")
