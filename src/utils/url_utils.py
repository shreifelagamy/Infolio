import requests
from bs4 import BeautifulSoup
import validators
from typing import Optional
from urllib.parse import urljoin

def validate_url(url: str) -> bool:
    """Validate if the given URL is properly formatted."""
    return validators.url(url) is True

def find_feed_url(url: str) -> Optional[str]:
    """
    Try to find RSS/Atom feed URL from a given website URL.
    Returns the feed URL if found, None otherwise.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for RSS/Atom feed links
        feed_links = soup.find_all('link', type=lambda t: t and ('rss' in t or 'atom' in t))
        
        if feed_links:
            feed_url = feed_links[0].get('href', '')
            # Handle relative URLs
            if not feed_url.startswith(('http://', 'https://')):
                feed_url = urljoin(url, feed_url)
            return feed_url
            
        # Alternative: look for 'a' tags containing 'rss' or 'feed'
        potential_feed_links = soup.find_all('a', href=True, text=lambda t: t and ('rss' in t.lower() or 'feed' in t.lower()))
        if potential_feed_links:
            feed_url = potential_feed_links[0]['href']
            if not feed_url.startswith(('http://', 'https://')):
                feed_url = urljoin(url, feed_url)
            return feed_url
            
    except Exception as e:
        print(f"Error finding feed for {url}: {str(e)}")
    return None
