import streamlit as st
from models import Post
from services.post_service import PostService

@st.dialog("Post Details", width="large")
def show_post_dialog(post: Post, post_service: PostService):
    """Show dialog for reading a post"""

    st.title(post.title)
    st.caption(f"Source: {post.source.name}")

    if post.image_url:
        st.image(post.image_url)

    st.markdown(post.description or post.summary or "No content available")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Open Original"):
            st.markdown(f"[Read Original Article]({post.external_link})")

    with col2:
        if st.button("Mark as Read"):
            post_service.mark_post_as_read(post.id)
            st.success("Marked as read!")
