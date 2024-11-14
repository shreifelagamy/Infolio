from typing import List
import feedparser

import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from models.article_model import Articles
from models.link_model import Links
from scrapper import scrapper_articles


def find_feed_urls(url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for RSS/Atom feed links
        feed_urls = []

        # Check link tags
        for link in soup.find_all('link'):
            if link.get('type') in ['application/rss+xml',
                                  'application/atom+xml',
                                  'application/feed+xml']:
                feed_url = urljoin(url, link.get('href', ''))
                return feed_url

        # Check a tags
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if 'feed' in href or 'rss' in href or 'atom' in href:
                feed_url = urljoin(url, href)
                return feed_url

        return None
    except Exception as e:
        st.error(f"Error checking {url}: {str(e)}")
        return None


@st.dialog("Scraping Progress", width="large")
def handle_scraping(urls: List[str], links_model: Links, articles_model: Articles):
    st.subheader("🔄 Scraping Progress")

    # URL Scraping Progress
    url_progress = st.progress(0, "Overall URLs Progress")

    for index, url in enumerate(urls):
        # Check if the URL is already a feed
        if any(feed_type in url for feed_type in ['rss', 'atom', 'feed']):
            rss_url = url
        else:
            rss_url = find_feed_urls(url)

        with st.status(f"🔍 Extracting feeds from {url}"):
            if rss_url:
                st.success(f"✅ Found RSS feed: {rss_url}")
            else:
                st.warning(f"❌ No RSS feed found for {url}")

            links_model.save_link(url, rss_url)

            try:
                source = url.split('/')[2]
                # Pass True if RSS URL is found, False otherwise
                records = scrape_single_url(rss_url if rss_url else url, source, is_feed=bool(rss_url))

                if records and records['articles']:
                    st.write(f"Found {len(records['articles'])} articles from {source}")
                    db_progress = st.progress(0, f"Saving articles from {source}")

                    for i, article in enumerate(records['articles']):
                        save_scraped_article(article, source, articles_model)
                        db_progress.progress((i + 1) / len(records['articles']))

                    st.success(f"✅ Completed saving articles from {source}")

            except Exception as e:
                st.error(f"❌ Error scraping {url}: {str(e)}")

        url_progress.progress((index + 1) / len(urls))

def extract_picture_links(entry: dict) -> List[str]:
    picture_links = [entry.get('media_content', [{}])[0].get('url', '')] if 'media_content' in entry else []
    if not picture_links:
        soup = BeautifulSoup(entry.get('description', ''), 'html.parser')
        img_tag = soup.find('img')
        if img_tag:
            picture_links = [img_tag.get('src', '')]
    return picture_links

def scrape_single_url(url: str, source: str, is_feed: bool = False) -> dict:
    with st.spinner(f'Scraping articles from {source}...'):
        if is_feed:
            try:
                feed = feedparser.parse(url)
                if feed.entries:
                    articles = []
                    for entry in feed.entries:
                        article = {
                            'title': entry.get('title', ''),
                            'description': entry.get('description', entry.get('summary', '')),
                            'link': entry.get('link', ''),
                            'picture_links': extract_picture_links(entry)
                        }
                        articles.append(article)
                    return {'articles': articles}
                else:
                    st.warning("No entries found in the feed")
                    return {'articles': []}
            except Exception as e:
                st.error(f"Error parsing feed: {str(e)}")
                return {'articles': []}
        else:
            records = scrapper_articles(url)
            st.json(records)
            return records

def save_scraped_article(article: dict, source: str, articles_model: Articles):
    image_urls_str = ','.join(article['picture_links']) if article['picture_links'] else None
    # Get only the first line of the title if it contains multiple lines
    title = article['title'].split('\n')[0].strip() if article['title'] else ''
    # Use title as description if description is None or empty
    description = article['description'] if article['description'] else article['title']

    articles_model.save_article(
        title=title,
        description=description,
        url=article['link'],
        image_urls=image_urls_str,
        source=source
    )