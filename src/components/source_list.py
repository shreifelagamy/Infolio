import streamlit as st
from services.source_service import SourceService

class SourceList:
    def __init__(self, source_service: SourceService):
        self.source_service = source_service

    def render(self):
        """Render the source list with delete buttons"""
        sources = self.source_service.get_all_sources()

        if not sources:
            st.info("No sources added yet. Add your first source above!")
            return

        for source in sources:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"### {source.name}")
                    st.markdown(f"**URL:** {source.url}")
                    st.markdown(f"**Feed URL:** {source.feed_url}")

                with col2:
                    if st.button("Refresh", key=f"refresh{source.id}", icon=":material/refresh:"):
                        success, message = self.source_service.refresh_source_posts(source)
                        if success:
                            st.toast(body=message, icon=":material/thumb_up:")
                        else:
                            st.toast(body=message, icon="🚨")

                with col3:
                    if st.button("Delete", key=f"delete{source.id}", type="primary", icon=":material/delete:"):
                        if st.session_state.get(f"confirm_delete_{source.id}", False):
                            # Confirmed delete
                            if self.source_service.delete_source(source.id):
                                st.toast(f"Source '{source.name}' deleted successfully!", icon=":material/delete:")
                                st.rerun()
                            else:
                                st.toast("Failed to delete source. Please try again.", icon="🚨")
                        else:
                            # Show confirmation
                            st.session_state[f"confirm_delete_{source.id}"] = True
                            st.toast(f"Are you sure you want to delete '{source.name}'?\n Click Delete again to confirm.", icon=":material/question_mark:")

                st.divider()
