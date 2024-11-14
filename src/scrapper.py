#!/usr/bin/env python3

import streamlit as st
import agentql
from playwright.sync_api import sync_playwright

ARTICLES_QUERY = """
{
    articles[] {
        title
        description
        link
        picture_links[]
    }
}
"""

def scrapper_articles(url):
    with sync_playwright() as playwright, playwright.chromium.launch(headless=True) as browser:
        # Create a new page in the browser and wrap it get access to the AgentQL's querying API
        page = agentql.wrap(browser.new_page())
        page.goto(url)

        articles_data = page.query_data(ARTICLES_QUERY)

        # Used only for demo purposes. It allows you to see the effect of the script.
        page.wait_for_timeout(10000)

        st.json(articles_data)
        return articles_data