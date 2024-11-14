#!/usr/bin/env python3

import agentql
from agentql.ext.playwright.sync_api import Page
from playwright.sync_api import sync_playwright

ARTICLES_QUERY = """
{
    articles[] {
        title
        description
        article_link
        image_link
    }
}
"""

def scrapper_articles(url):
    with sync_playwright() as playwright, playwright.chromium.launch(headless=False) as browser:
        # Create a new page in the browser and wrap it get access to the AgentQL's querying API
        page = agentql.wrap(browser.new_page())
        page.goto(url)

        articles_data = page.query_data(ARTICLES_QUERY)

        print(articles_data)