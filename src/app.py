import streamlit as st
from database import DatabaseManager
from services.post_service import PostService
from services.source_service import SourceService
from components.source_form import SourceForm
from pages import posts, sources

# Initialize database and services
db = DatabaseManager()
post_service = PostService(db)
source_service = SourceService(db, post_service)

# Initialize source form for sidebar
source_form = SourceForm(source_service)

def main():
    # Configure the app
    st.set_page_config(
        page_title="Content Aggregator",
        page_icon="📰",
        layout="wide"
    )

    # Add source form to sidebar
    with st.sidebar:
        st.header("Add New Source")
        source_form.render()

    # Setup navigation
    page = st.navigation([
        st.Page(
            "pages/posts.py",
            title="Latest Posts",
            icon="📚",
            default=True
        ),
        st.Page(
            "pages/sources.py",
            title="Manage Sources",
            icon="⚙️"
        ),
    ])

    # Run the selected page
    page.run()

if __name__ == "__main__":
    main()