"""Source form component for adding new content sources"""

import streamlit as st

from services.source_service import SourceService
from utils.url_utils import find_feed_url, validate_url


class SourceForm:
    """Form component for adding new content sources"""

    def __init__(self, source_service: SourceService):
        """Initialize source form with source service"""
        self.source_service = source_service
        # Initialize session state for form fields if they don't exist
        if 'source_url' not in st.session_state:
            st.session_state.source_url = ""
        if 'source_name' not in st.session_state:
            st.session_state.source_name = ""

    def _reset_form(self):
        """Reset form fields"""
        st.session_state.source_url = ""
        st.session_state.source_name = ""
        st.session_state.loading = False

    @st.fragment()
    def render(self):
        """Render the source form"""
        with st.form("source_form"):
            # Form fields
            url = st.text_input("Source URL *", key="source_url")
            name = st.text_input("Source Name *", key="source_name")

            # Submit button with loading state and icon
            if st.form_submit_button(label="Add Source", icon="🌟", type="primary", disabled=st.session_state.get("loading", False)):
                if not url or not name:
                    st.error("Please fill in all required fields")
                    return

                st.session_state.loading = True

                with st.spinner("Adding source..."):
                    try:
                        # Validate URL
                        if not validate_url(url):
                            st.error("Please enter a valid URL")
                            st.session_state.loading = False
                            return

                        # Try to find feed URL
                        feed_url = find_feed_url(url)

                        # Check if source already exists
                        if self.source_service.check_source_exists(url, feed_url):
                            st.error("This source has already been added")
                            st.session_state.loading = False
                            return

                        # Add the source
                        source = self.source_service.add_source(url, feed_url, name)

                        # Show success message with source details
                        st.success(
                            f"Successfully added source:\n\n"
                            f"- URL: [{source.url}]({source.url})\n"
                            f"- Feed: {f'[{source.feed_url}]({source.feed_url})' if source.feed_url else 'Not provided'}\n"
                            f"- Name: {source.name or 'Not provided'}"
                        )

                        # Reset form after successful submission
                        self._reset_form()
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error adding source: {str(e)}")
                        st.session_state.loading = False
