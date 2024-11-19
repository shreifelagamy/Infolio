import math
import webbrowser
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st
from bs4 import BeautifulSoup

from models.article_model import Articles

from .linkedin_post_dialog import show_linkedin_post_dialog


def setup_page_style():
    st.markdown("""
        <style>
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            margin: 20px 0;
        }
        .pagination-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
        }
        .page-info {
            color: #666;
            font-size: 0.9em;
        }
        .items-info {
            color: #666;
            font-size: 0.9em;
            margin-left: 10px;
        }
        /* Hide the default Streamlit button margins */
        .stButton {
            display: inline-block;
            margin: 0 5px;
        }

        /* Enhanced pagination button styles */
        .stButton button[kind="secondary"] {
            width: 100%;
            background-color: transparent;
            border: 1px solid #e0e0e0;
            color: #666;
            font-size: 0.9em;
            padding: 0.5em 1em;
            transition: all 0.3s ease;
        }

        .stButton button[kind="secondary"]:hover {
            background-color: #f8f9fa;
            border-color: #666;
            color: #1a1a1a;
        }
        </style>
    """, unsafe_allow_html=True)

def setup_article_styles():
    st.markdown("""
        <style>
            .source-tag {
                display: inline-block;
                background-color: #dfe6e9;
                padding: 4px 8px;
                border-radius: 0;
                font-size: 0.8em;
                color: #2d3436;
                margin-bottom: 10px;
                margin-right: 5px;
            }
            .id-tag {
                display: inline-block;
                background-color: #e0e0e0;
                padding: 4px 8px;
                border-radius: 0;
                font-size: 0.8em;
                color: #2d3436;
                margin-bottom: 10px;
                margin-right: 5px;
            }
            .date-tag {
                display: inline-block;
                background-color: #74b9ff;
                padding: 4px 8px;
                border-radius: 0;
                font-size: 0.8em;
                color: #2d3436;
                margin-bottom: 10px;
            }
            .status-tag {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 0;
                font-size: 0.8em;
                margin-bottom: 10px;
                margin-right: 5px;
            }
            .read-tag {
                background-color: #00b894;
                color: #ffffff;
            }
            .unread-tag {
                background-color: #ff7675;
                color: #ffffff;
            }
            /* Add smooth transitions */
            .stButton>button {
                transition: all 0.3s ease;
            }
        </style>
    """, unsafe_allow_html=True)

def display_pagination_controls(current_page: int, total_pages: int, total_items: int, per_page: int, filter_value: str):
    start_item = (current_page - 1) * per_page + 1
    end_item = min(current_page * per_page, total_items)

    # Create columns for pagination items
    prev_col, pages_col, next_col = st.columns([1, 4, 1])

    with prev_col:
        if current_page > 1:
            if st.button(
                "← Previous",
                key=f"prevpage{filter_value}",
                use_container_width=True,
                type="primary",
            ):
                st.session_state.current_page = current_page - 1
                st.rerun()

    with pages_col:
        # Create dynamic columns based on total pages
        page_cols = st.columns(min(total_pages, 7))  # Limit to 7 pages to avoid overcrowding

        for idx, col in enumerate(page_cols):
            with col:
                page_num = idx + 1
                button_type = "primary" if page_num == current_page else "secondary"
                if st.button(
                    f"{page_num}",
                    key=f"page{page_num}{filter_value}",
                    type=button_type,
                    use_container_width=True,
                ):
                    st.session_state.current_page = page_num
                    st.rerun()

        st.markdown(
            f'<div style="text-align: center;">'
            f'<span class="items-info">({start_item}-{end_item} of {total_items} items)</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    with next_col:
        if current_page < total_pages:
            if st.button(
                "Next →",
                key=f"nextpage{filter_value}",
                use_container_width=True,
                type="primary",
            ):
                st.session_state.current_page = current_page + 1
                st.rerun()

def display_articles():
    articles_model = Articles()

    # Initialize pagination state
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    # Replace segmented control with tabs
    filter_options = {
        "All": None,
        "Read": "read",
        "Favorites": "favorites"
    }
    selected_tab = st.tabs(list(filter_options.keys()))

    # Reset page when switching tabs
    for i, tab in enumerate(selected_tab):
        with tab:
            filter_value = filter_options[list(filter_options.keys())[i]]

            # Get pagination data with filter
            per_page = 12
            total_articles = articles_model.get_total_filtered_articles(filter_value)
            total_pages = math.ceil(total_articles / per_page)

            # Reset page if it exceeds the new total pages
            if st.session_state.current_page > total_pages:
                st.session_state.current_page = 1

            current_page = st.session_state.current_page

            # Get filtered and paginated articles
            articles = articles_model.get_filtered_articles(
                current_page,
                per_page,
                filter_value
            )

            # Display articles in grid with 3 columns
            if articles:
                cols = st.columns(3)
                for idx, article in enumerate(articles):
                    display_article_card(article, cols[idx % 3], filter_value)

                # Display pagination controls with total items
                display_pagination_controls(current_page, total_pages, total_articles, per_page, filter_value)
            else:
                st.info("No articles found for the selected filter.")

def display_article_card(record: Dict[str, Any], col, filter_value: str):
    articles_model = Articles()

    with col:
        with st.container(border=True):
            # Add read status tag before other tags
            is_read = bool(record.get('is_read', 0))
            status_tag = (
                f'<div class="status-tag read-tag">✓ Read</div>' if is_read
                else f'<div class="status-tag unread-tag">📖 Unread</div>'
            )

            # Create two columns for toggle and date
            toggle_col, date_col = st.columns([0.6, 0.4])

            with toggle_col:
                # Initialize toggle with DB value and handle changes
                is_read = st.toggle("Mark as read",
                                key=f"read{record['id']}{filter_value}",
                                value=bool(record.get('is_read', 0)),
                                on_change=lambda: articles_model.toggle_read_status(record['id']))

            with date_col:
                # Convert scraped_date to human readable format
                date_obj = datetime.strptime(record['scraped_date'], '%Y-%m-%d %H:%M:%S')
                formatted_date = date_obj.strftime('%B %d, %Y')
                st.markdown(f"<div style='padding-top: 5px;'>{formatted_date}</div>", unsafe_allow_html=True)

            if record['image_urls']:
                st.image(record['image_urls'], use_column_width=True)

            st.subheader(record['title'], anchor=None)
            st.markdown(
                f'{status_tag}'
                f'<div class="source-tag">{record["source"]}</div>'
                f'<div class="id-tag">ID: {record["id"]}</div>',
                unsafe_allow_html=True
            )

            description = record['description']
            if description:
                # Parse the description HTML and extract the first paragraph
                text_only = BeautifulSoup(description, 'html.parser').getText()
                # Remove 'Read more' text if it exists
                text_only = text_only.replace('Read more', '').strip()
                st.markdown(text_only[:200] if len(text_only) > 200 else text_only)

            _col1, _col2, _col3, _col4 = st.columns([0.15, 0.15, 0.15, 0.55])

            with _col1:
                if record['url']:
                    if st.button("🔗", help="open article in browser", key=f"link{record['id']}{filter_value}"):
                        webbrowser.open_new_tab(record['url'])
                        articles_model.read(record['id'])
                        st.rerun()
            with _col2:
                if st.button(
                    label= "📂",
                    help="post on linkedin",
                    key=f"linkedin{record['id']}{filter_value}",
                ):
                    show_linkedin_post_dialog(record)
            with _col3:
                is_favorite = bool(record.get('is_favorite', 0))
                favorite_icon = "❤️" if is_favorite else "💔"
                if st.button(
                    label=favorite_icon,
                    help="toggle favorite",
                    key=f"favorite{record['id']}{filter_value}",
                ):
                    articles_model.toggle_favorite_status(record['id'])