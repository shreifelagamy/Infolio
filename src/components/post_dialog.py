import streamlit as st

@st.dialog("Example title", width="large")
def show_post_dialog(post):
    st.markdown(f"## {post.title}")
    st.markdown(f"📰 {post.source.name} • 📅 {post.published_date.strftime('%Y-%m-%d %H:%M') if post.published_date else 'No date'}")
    st.markdown(post.description, unsafe_allow_html=True)
