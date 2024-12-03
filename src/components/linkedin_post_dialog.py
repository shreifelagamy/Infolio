import streamlit as st
from models import Post
from services.linkedin_service import LinkedInService

@st.dialog("Generate LinkedIn Post", width="large")
def show_linkedin_post_dialog(post: Post, linkedin_service: LinkedInService):
    """Show dialog for LinkedIn post generation"""

    # Show article details
    st.markdown(f"### Article: {post.title}")
    st.caption(f"Source: {post.source.name}")

    # User preferences
    preferences = st.text_area(
        "Any specific preferences for the post?",
        placeholder="E.g., 'Focus on technical aspects' or 'Keep it business-oriented'",
        help="Optional: Add any specific preferences for the LinkedIn post"
    )

    if st.button("Generate Post"):
        with st.spinner("Generating LinkedIn post..."):
            result = linkedin_service.generate_linkedin_post(post, preferences)

            # Show the generated post
            st.markdown("### Generated LinkedIn Post")
            post_content = st.text_area(
                "Edit the post if needed:",
                value=result,
                height=300
            )

            # Get the latest LinkedIn post for this article
            linkedin_posts = linkedin_service.get_linkedin_posts(post.id)
            current_post = linkedin_posts[0] if linkedin_posts else None

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Draft"):
                    if current_post:
                        linkedin_service.update_linkedin_post(current_post.id, post_content)
                    st.success("Draft saved!")

            with col2:
                if st.button("Mark as Published"):
                    if current_post:
                        linkedin_service.publish_linkedin_post(current_post.id)
                    st.success("Post marked as published!")

    # Show chat history
    st.markdown("### Generation History")
    chat_history = linkedin_service.get_post_history(post.id)

    for chat in chat_history:
        with st.chat_message(chat.role):
            st.write(chat.content)
            st.caption(f"Time: {chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
