import streamlit as st
from services.source_service import SourceService
from utils.url_utils import validate_url, find_feed_url

class SourceForm:
    def __init__(self, source_service: SourceService):
        self.source_service = source_service

    def render(self):
        with st.form("add_source_form"):
            url = st.text_input("Enter website URL")
            name = st.text_input("Source Name (optional)")
            submitted = st.form_submit_button("Add Source")

            if submitted and url:
                self._handle_source_submission(url, name)

    def _handle_source_submission(self, url: str, name: str):
        if not validate_url(url):
            st.error("Please enter a valid URL")
            return

        # Try to find feed URL
        feed_url = find_feed_url(url)

        # Check if source already exists
        try:
            if self.source_service.check_source_exists(url, feed_url):
                st.error("This source has already been added")
                return
        except Exception as e:
            st.error(f"Error checking source: {str(e)}")
            return

        # Add to database
        try:
            success, message = self.source_service.add_source(url, feed_url, name)
            if success:
                st.success(message)
                if feed_url:
                    st.info(f"Found RSS feed: {feed_url}")
            else:
                st.error(message)
        except Exception as e:
            st.error(f"Error adding source: {str(e)}")
