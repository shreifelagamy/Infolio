import streamlit as st

from handlers.scraping_handler import handle_scraping
from models.article_model import Articles
from models.link_model import Links
from ui.components import (display_articles, setup_article_styles,
                           setup_page_style)

st.set_page_config(
    layout="wide",
    page_title="Articles Reader",
    page_icon="📚",
    initial_sidebar_state="expanded"
)

def main():
    st.title("Articles")
    setup_page_style()
    setup_article_styles()

    links_model = Links()
    articles_model = Articles()

    try:
        # Setup scraping interface in sidebar
        with st.sidebar:
            st.header("Scraping Interface")
            links = [link[0] for link in links_model.get_all_links()]
            links_input = st.text_area('Links to scrape', value='\n'.join(links))

            if st.button(label='Find RSS Feeds', type='secondary'):
                links_model.clear_links()
                urls = [url.strip() for url in links_input.split('\n') if url.strip()]

                if urls:
                    handle_scraping(urls, links_model, articles_model)
                else:
                    st.warning("Please enter some URLs to check for RSS feeds")


            st.divider()  # Add a visual separator
            if st.button("Integrate Medium", icon=":material/article:"):
                st.info("Medium integration functionality to be implemented")

        # Display articles with pagination
        display_articles()

    finally:
        links_model.close_conn()
        articles_model.close_conn()

if __name__ == "__main__":
    main()
