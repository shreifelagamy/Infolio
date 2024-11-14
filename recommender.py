from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from models import ArticleDatabase
from dotenv import load_dotenv
import os

class ContentRecommender:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7
        )  # LangChain will automatically use OPENAI_API_KEY from env
        self.db = ArticleDatabase()

    def get_recommendation(self):
        # Get all articles from database
        articles = self.db.get_all_articles()

        # Prepare context
        context = "Based on the following articles:\n\n"
        for article in articles[:5]:  # Limit to last 5 articles for context
            context += f"Title: {article[1]}\nSummary: {article[2][:500]}...\n\n"

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a content strategy expert specialized in identifying content gaps and opportunities."),
            ("user", """{context}
            Please analyze these articles and suggest:
            1. A unique topic for a new article that would complement existing content
            2. Key points to cover
            3. Why this topic would be valuable to readers

            Format your response in a structured way with clear headings and bullet points.""")
        ])

        # Create the chain
        chain = prompt | self.llm | StrOutputParser()

        # Execute the chain
        recommendation = chain.invoke({"context": context})

        return recommendation