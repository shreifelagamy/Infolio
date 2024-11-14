from crewai import LLM, Agent, Crew, Task

from web_scraper import WebScraper

content_extractor = Agent(
    role="HTML Content Extractor",
    goal="""
        extract important topic, that seems like articles from html code, extract should include title, description and link
    """,
    backstory="""
    •	A data-focused web content analyzer, trained to recognize common web structures and extract the main content of interest.
	•	Developed with the purpose of isolating significant information (titles, descriptions, links, images) from cluttered HTML, making it easy for the next agent to organize this data.
    """,
    allow_delegation=False,
    verbose=False,
    llm=LLM(model="ollama/llama3.1:8b", base_url="http://localhost:11434")
)

# data_origanizer = Agent(
#     role="Content Organizer and Tagging Agent",
#     goal="""
#     •	Receive the extracted data and reorganize it into a structured JSON format.
# 	•	Analyze each article’s content to identify relevant tags (e.g., PHP, packages, tutorials, etc.) based on topic and keywords, adding metadata for easy categorization.
#     """,
#     backstory="""
#     •	An AI-driven content classifier and organizer, trained in topic identification and JSON structuring.
# 	•	Purpose-built to assist in preparing web content for structured storage or display, leveraging contextual cues to assign accurate tags for each piece of content.
#     """,
#     verbose=True,
#     allow_delegation=False
# )

def create_task(content):
    return Task(
        name="Get published articles",
        description=f"""
            I want to extract what seems to be important articles in the below html

            {content}
        """,
        agent=content_extractor,
        expected_output="list titles",

    )

def main():
    web_scraper = WebScraper('https://laravel-news.com/blog')
    # Fetch and clean content
    content = web_scraper.fetch_content(clean=True, minify=True)

    # print(content)

    task = create_task(content);

    crew = Crew(
        agents=[content_extractor],
        tasks=[task]
    )

    result = crew.kickoff()
    print(result)
if __name__ == "__main__":
    main()
