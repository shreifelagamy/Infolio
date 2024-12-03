import streamlit as st
from services.source_service import SourceService

class SourceList:
    def __init__(self, source_service: SourceService):
        self.source_service = source_service

    def render(self):
        st.subheader("Current Sources")
        sources = self.source_service.get_all_sources()
        
        if not sources:
            st.info("No sources added yet")
            return
        
        # Create columns for the table header
        cols = st.columns([3, 2, 2, 1])
        cols[0].write("**Source**")
        cols[1].write("**Feed URL**")
        cols[2].write("**Last Checked**")
        cols[3].write("**Actions**")
        
        # Display each source with a refresh button
        for source in sources:
            cols = st.columns([3, 2, 2, 1])
            cols[0].write(source.name or source.url)
            cols[1].write(source.feed_url or "Not found")
            cols[2].write(source.last_checked.strftime("%Y-%m-%d %H:%M") if source.last_checked else "Never")
            
            # Add refresh button
            if cols[3].button("🔄", key=f"refresh_{source.id}"):
                with st.spinner(f"Refreshing posts from {source.name or source.url}..."):
                    success, message = self.source_service.refresh_source_posts(source)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
