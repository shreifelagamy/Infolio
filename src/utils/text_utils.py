from bs4 import BeautifulSoup

def clean_html(html_text: str) -> str:
    """Remove HTML tags and clean up the text."""
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup.get_text(separator=' ', strip=True)
