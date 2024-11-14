import os
import re
import time
from typing import Any, Dict, Literal, Optional

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class LinkedInPostResponse(BaseModel):
    response_type: Literal["chat", "post_update"]
    message: str
    updated_post: Optional[str] = None

def get_ai_response(messages: list, article: Dict[str, Any]) -> LinkedInPostResponse:
    # Add system message with context
    system_message = {
        "role": "system",
        "content": f"""You are a professional LinkedIn post writer. Help the user create engaging posts about articles they've read.
        Current article:
        Title: {article['title']}
        Description: {article['description']}
        URL: {article['url']}

        First, try to access the URL to get the full content of the article. If you can access the link, use the full content to generate the post. If you cannot access the link, indicate in your response that you were unable to access the link and generate the post based on the provided title and description.

        When suggesting post updates, set response_type to "post_update" and include the full post in updated_post.

        The full post should be in plain text without any markdown or HTML tags. Emojis can be included if requested.

        By default, include the article link in the content. If the user requests not to include it, you can omit the link.

        For general chat responses, set response_type to "chat"."""
    }

    # Prepare messages for API call
    api_messages = [system_message] + messages

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": m["role"], "content": m["content"]} for m in api_messages],
        temperature=0.7,
        response_format=LinkedInPostResponse,
    )

    return completion.choices[0].message.parsed

def is_rtl(text: str) -> bool:
    """Detect if text contains RTL characters (Arabic, Hebrew, etc)"""
    rtl_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\u0590-\u05FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(rtl_pattern.search(text))

@st.dialog("Generate LinkedIn Post")
def show_linkedin_post_dialog(article: Dict[str, Any]):
    # Add custom CSS for responsive dialog and RTL support
    st.markdown("""
        <style>
        [role="dialog"] {
            max-width: min(90vw, 1200px) !important;
            width: 90vw !important;
        }

        /* Stack columns on smaller screens */
        @media (max-width: 768px) {
            .stColumns {
                flex-direction: column;
            }
            .stColumn {
                width: 100% !important;
            }
        }

        /* RTL support */
        .rtl-text {
            direction: rtl !important;
            text-align: right !important;
        }

        .rtl-text textarea {
            direction: rtl !important;
            text-align: right !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "final_post" not in st.session_state:
        st.session_state.final_post = _generate_default_post(article)

    # Determine layout based on screen width
    screen_width = st.session_state.get('screen_width', 1200)
    use_columns = screen_width > 768

    if use_columns:
        chat_col, post_col = st.columns(2)
    else:
        chat_col = post_col = st

    with chat_col:
        st.subheader("Chat History")
        # Adjust container height for mobile
        container_height = 600 if use_columns else 400
        messages = st.container(height=container_height)

        for chat_history in st.session_state.chat_history:
            with messages.chat_message(chat_history["role"]):
                st.markdown(chat_history["content"])

        st.markdown("""
        <style>
            .st-key-chatinput textarea {
                direction: rtl; /* Set the text direction to right-to-left for Arabic */
                unicode-bidi: isolate; /* Ensure that the text is treated as a single unit */
            }

            .st-key-chatinput textarea * {
                direction: ltr; /* Set the direction to left-to-right for English text */
                unicode-bidi: embed; /* Embed the English text within the Arabic text */
            }
        </style>
        """, unsafe_allow_html=True)

        # Chat input
        if user_input := st.chat_input("Type your message...", key="chatinput"):
            # Add user message to chat history
            with messages.chat_message("user"):
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.markdown(user_input)

            with messages.chat_message("assistant"):
                message = st.empty()

                with message.status("Thinking..."):
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": "I will try to help you!"}
                    )
                    time.sleep(5)

                # Determine the language based on the count of assistant messages
                assistant_message_count = sum(1 for msg in st.session_state.chat_history if msg["role"] == "assistant")
                if assistant_message_count % 2 == 0:
                    st.session_state.final_post = f"""🔍 قراءة ممتعة: {article['title']}"""
                else:
                    st.session_state.final_post = f"""🔍 Enjoyable Read: {article['title']}"""

                message.markdown("I will try to help you!")
            # _show_chat_messages(messages)
            # st.rerun()

            # Get AI response
            # ai_response = get_ai_response(st.session_state.chat_history, article)

            # # # Add AI response to chat history
            # if ai_response.response_type == 'chat':
            #     st.session_state.chat_history.append(
            #         {"role": "assistant", "content": ai_response.message}
            #     )

            # # Update the final post if AI provides an update
            # if ai_response.response_type == "post_update" and ai_response.updated_post:
            #     st.session_state.final_post = ai_response.updated_post

    with post_col:
        st.subheader("Final LinkedIn Post")

        # Check if content is RTL
        is_rtl_content = is_rtl(st.session_state.final_post)

        # Wrap text area in a div with RTL class if needed
        if is_rtl_content:
            st.markdown("""
            <style>
                .st-key-editpost {
                    direction: rtl !important;
                    text-align: right !important;
                }
            </style>
            """, unsafe_allow_html=True)

        # Adjust text area height for mobile
        text_area_height = 300 if use_columns else 200
        st.session_state.final_post = st.text_area(
            "Edit your post",
            value=st.session_state.final_post,
            height=text_area_height,
            key="editpost"
        )

        if st.button("", icon=":material/file_copy:", type="primary", help="Copy post to clipboard"):
            st.success("Post copied to clipboard!", icon="👍")

        # Preview section with RTL support
        st.subheader("Preview")

        if is_rtl_content:
            st.markdown("""
            <style>
                .st-key-linkedinpreview {
                    direction: rtl !important;
                    text-align: right !important;
                }
            </style>
            """, unsafe_allow_html=True)

        with st.container(height=200, key="linkedinpreview"):
            st.markdown(st.session_state.final_post)

def _generate_default_post(article: Dict[str, Any]) -> str:
    return f"""🔍 قراءة ممتعة: {article['title']}

النقاط الرئيسية:
{article['description'][:200] + '...' if len(article['description']) > 200 else article['description']}

اقرأ المزيد: {article['url']}

#تكنولوجيا #ابتكار #تعلم"""