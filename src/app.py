import streamlit as st

from components.source_form import SourceForm
from database import DatabaseManager
from services.post_service import PostService
from services.source_service import SourceService

st.set_page_config(layout="wide")

# Initialize services
db = DatabaseManager()
post_service = PostService(db)
source_service = SourceService(db, post_service)

# Add source form to sidebar
with st.sidebar:
    st.header("Add New Source")
    source_form = SourceForm(source_service)
    source_form.render()

pages = st.navigation([
    st.Page(page="views/posts.py", title="Latest Posts", icon="📰", default=True),
    st.Page(page="views/sources.py", title="Sources", icon="📚"),
])

pages.run();