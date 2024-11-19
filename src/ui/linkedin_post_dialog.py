import re
import time
from typing import Any, Dict

import streamlit as st

from models.chat_model import Chat
from utils.gpt_integration import GPTIntegration, LinkedInPostResponse


def get_ai_response(messages: list, article: Dict[str, Any]) -> LinkedInPostResponse:
    gpt_integration = GPTIntegration()
    return gpt_integration.get_ai_response(messages, article)

def is_rtl(text: str) -> bool:
    """Detect if text contains RTL characters (Arabic, Hebrew, etc)"""
    rtl_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\u0590-\u05FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(rtl_pattern.search(text))

@st.dialog("Share your knowledge on LinkedIn", width=1200)
def show_linkedin_post_dialog(article: Dict[str, Any]):
    # Simplified CSS for dialog
    st.markdown("""
        <style>
        [role="dialog"] {
            max-width: min(90vw, 1200px) !important;
            width: 90vw !important;
        }
        </style>
    """, unsafe_allow_html=True)

    chat_model = Chat()
    article_id = article.get('id')

    # Initialize chat history and final post
    if article_id:
        chat_records = chat_model.get_chats_by_article(article_id)
        st.session_state.chat_history = [
            {"role": "user", "content": record["user_message"]} if record["user_message"] else
            {"role": "assistant", "content": record["assistant_message"]}
            for record in chat_records
        ]
        if chat_records:
            st.session_state.final_post = next((record['generated_post'] for record in reversed(chat_records) if record['generated_post']), '')

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "final_post" not in st.session_state:
        st.session_state.final_post = ""

    # Main content columns
    chat_col, post_col = st.columns(2)

    with chat_col:
        _post_reviewer(article)

    with post_col:
        _generate_post_area(chat_model=chat_model, article_id=article_id)

        _render_chat_interface(article, chat_model, article_id)

    chat_model.close_conn()

def _render_chat_interface(article, chat_model, article_id):
    st.subheader("Chat with AI")
    messages = st.container(height=400)

    for chat_history in st.session_state.chat_history:
        with messages.chat_message(chat_history["role"]):
            st.markdown(chat_history["content"])

    if user_input := st.chat_input("Type your message...", key="chatinput"):
        with messages.chat_message("user"):
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.markdown(user_input)

        chat_model.save_chat(article_id=article_id, user_message=user_input)

        with messages.chat_message("assistant"):
            message = st.empty()
            with message.status("Thinking..."):
                st.session_state.chat_history.append(
                        {"role": "assistant", "content": "I will try to help you!"}
                    )
                time.sleep(5)

            assistant_message_count = sum(1 for msg in st.session_state.chat_history if msg["role"] == "assistant")
            st.session_state.final_post = f"""🔍 {'قراءة ممتعة' if assistant_message_count % 2 == 0 else 'Enjoyable Read'}: {article['title']}"""

            message.markdown("I will try to help you!")
            chat_model.save_chat(
                    article_id=article_id,
                    assistant_message="I will try to help you!",
                    generated_post=st.session_state.final_post
                )

def _post_reviewer(article):
    st.markdown("""
    <style>
        .st-key-articlepreiview {
            width: 100%;
            height: 100%;
            overflow-y: auto;
            padding: 0;
        }
        .st-key-articlepreiview > div {
            width: 100% !important;
            max-width: 100% !important;
            word-wrap: break-word;
        }
        .st-key-articlepreiview iframe,
        .st-key-articlepreiview img {
            max-width: 100%;
            height: auto;
        }
    </style>
    """, unsafe_allow_html=True)

    st.header(article['title'])
    with st.container(height=700, key="articlepreiview"):
        st.html(article['description'])

def _generate_post_area(chat_model: Chat, article_id: str):
    st.subheader("LinkedIn Post")
    is_rtl_content = is_rtl(st.session_state.final_post)

    if is_rtl_content:
        st.markdown("""
        <style>
            .st-key-editpost {
                direction: rtl !important;
                text-align: right !important;
            }
        </style>
        """, unsafe_allow_html=True)

    st.session_state.final_post = st.text_area(
        "Edit your post",
        placeholder="Your generated post will be here...",
        height=100,
        key="editpost"
    )

    if st.button("", icon=":material/file_copy:", type="primary", help="Copy post to clipboard"):
        st.success("Post copied to clipboard!", icon="👍")
        chat_model.save_chat(article_id, "", "", st.session_state.final_post)

