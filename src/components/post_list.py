import streamlit as st
import os
from utils.text_utils import clean_html
from .post_dialog import show_post_dialog

class PostList:
    POSTS_PER_PAGE = 10
    IMAGE_WIDTH = 200
    IMAGE_HEIGHT = 150
    DEFAULT_IMAGE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "default_post.png")

    def __init__(self, post_service):
        self.post_service = post_service

    def render(self):
        st.subheader("Latest Posts")

        total_posts = self.post_service.get_total_posts_count()
        if total_posts == 0:
            st.info("No posts available yet")
            return

        current_page = self._render_pagination_controls(total_posts)
        posts = self._get_paginated_posts(current_page)
        self._render_posts(posts)

    def _render_pagination_controls(self, total_posts):
        total_pages = (total_posts + self.POSTS_PER_PAGE - 1) // self.POSTS_PER_PAGE

        col1, col2, col3 = st.columns([2, 4, 2])
        with col2:
            current_page = st.select_slider(
                "Page",
                range(1, total_pages + 1),
                value=1,
                key="page_slider"
            )

        st.caption(f"Showing page {current_page} of {total_pages} (Total posts: {total_posts})")
        return current_page

    def _get_paginated_posts(self, current_page):
        offset = (current_page - 1) * self.POSTS_PER_PAGE
        return self.post_service.get_posts(limit=self.POSTS_PER_PAGE, offset=offset)

    def _render_posts(self, posts):
        for post in posts:
            with st.container(border=True):
                cols = st.columns([2, 5])

                # Left column: Image
                with cols[0]:
                    if post.image_url:
                        st.image(
                            post.image_url,
                            width=self.IMAGE_WIDTH,
                            output_format="JPEG"
                        )
                    else:
                        st.image(
                            self.DEFAULT_IMAGE,
                            width=self.IMAGE_WIDTH,
                            output_format="PNG"
                        )

                # Right column: Content
                with cols[1]:
                    # Title row with read status
                    title_col, status_col = st.columns([4, 1])
                    with title_col:
                        st.markdown(f"### {post.title}")
                    with status_col:
                        if post.is_read:
                            st.markdown(
                                """
                                <div style="
                                    background-color: #28a745;
                                    color: white;
                                    padding: 5px 10px;
                                    border-radius: 15px;
                                    text-align: center;
                                    margin-top: 10px;
                                ">
                                    ✓ Read
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                """
                                <div style="
                                    background-color: #6c757d;
                                    color: white;
                                    padding: 5px 10px;
                                    border-radius: 15px;
                                    text-align: center;
                                    margin-top: 10px;
                                ">
                                    Unread
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    # Metadata row
                    st.caption(f"📰 {post.source.name} • 📅 {post.published_date.strftime('%Y-%m-%d %H:%M') if post.published_date else 'No date'}")

                    # Description
                    if post.description:
                        clean_description = clean_html(post.description)
                        description = clean_description[:300] + "..." if len(clean_description) > 300 else clean_description
                        st.markdown(f"*{description}*")

                    # Action buttons
                    col1, col2, col3 = st.columns([2, 2, 4])
                    with col1:
                        if st.button("Read Post →", key=f"read_post_{post.id}"):
                            # Mark as read if not already read
                            if not post.is_read:
                                self.post_service.mark_post_as_read(post.id)
                            # Open post in a dialog
                            show_post_dialog(post)
