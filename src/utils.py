import requests
from bs4 import BeautifulSoup
import feedparser
import validators
from typing import Optional, Tuple, List
from urllib.parse import urljoin
import time
from datetime import datetime

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

def parse_feed(feed_url: str) -> List[dict]:
    """
    Parse RSS/Atom feed and return list of posts.
    """
    try:
        feed = feedparser.parse(feed_url)
        posts = []
        
        for entry in feed.entries:
            # Handle the published date
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
            
            post = {
                'title': entry.get('title', ''),
                'description': entry.get('description', ''),
                'summary': entry.get('summary', ''),
                'link': entry.get('link', ''),
                'published_date': published_date
            }
            
            # Try to find image in the entry
            if 'media_content' in entry:
                media = entry.media_content[0]
                if 'url' in media:
                    post['image_url'] = media['url']
            elif 'content' in entry and entry.content:
                # Try to find image in content
                content_soup = BeautifulSoup(entry.content[0].value, 'html.parser')
                img = content_soup.find('img')
                if img and img.get('src'):
                    post['image_url'] = img['src']
            else:
                post['image_url'] = None
                
            posts.append(post)
            
        return posts
    except Exception as e:
        print(f"Error parsing feed {feed_url}: {str(e)}")
        return []
