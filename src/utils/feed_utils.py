import feedparser
import time
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List

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
