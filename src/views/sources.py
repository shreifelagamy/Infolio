import streamlit as st
from database import DatabaseManager
from services.post_service import PostService
from services.source_service import SourceService
from components.source_list import SourceList

st.title("Manage Content Sources")
st.markdown("""
View and manage your content sources here. You can refresh sources to fetch new content
or remove sources you no longer want to follow.
""")

# Initialize services
db = DatabaseManager()
post_service = PostService(db)
source_service = SourceService(db, post_service)

# Initialize and render source list
source_list = SourceList(source_service)
source_list.render()
