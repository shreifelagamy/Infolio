import os
from typing import Any, Dict, Literal, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

# Load environment variables
load_dotenv()

class LinkedInPostResponse(BaseModel):
    response_type: Literal["chat", "post_update"]
    message: str
    updated_post: Optional[str] = None

class GPTIntegration:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GPTIntegration, cls).__new__(cls)
            cls._instance.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return cls._instance

    def get_ai_response(self, messages: list, article: Dict[str, Any]) -> LinkedInPostResponse:
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

        api_messages = [system_message] + messages

        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": m["role"], "content": m["content"]} for m in api_messages],
            temperature=0.7,
            response_format=LinkedInPostResponse,
        )

        return completion.choices[0].message.parsed
