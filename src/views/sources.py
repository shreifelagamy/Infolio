import streamlit as st
from database import DatabaseManager
from services.post_service import PostService
from services.source_service import SourceService
from components.source_list import SourceList
from components.source_form import SourceForm

st.title("Manage Content Sources")
st.markdown("""
Add and manage your content sources here. Each source should have a valid RSS/Atom feed URL.
""")

# Initialize services
db = DatabaseManager()
post_service = PostService(db)
source_service = SourceService(db, post_service)

source_list = SourceList(source_service)
source_list.render()
