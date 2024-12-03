import streamlit as st
from database import DatabaseManager
from services.post_service import PostService
from components.post_list import PostList

st.title("Latest Posts")
st.markdown("""
Stay updated with the latest content from your favorite sources.
Add new sources using the sidebar!
""")

# Initialize services and components
db = DatabaseManager()
post_service = PostService(db)
post_list = PostList(post_service)

# Render posts
post_list.render()
