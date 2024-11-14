import requests
from bs4 import BeautifulSoup, Tag
import os

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.soup = None

    def clean_content(self, soup):
        """Remove all tags except body content and clean unwanted elements"""
        # Create a copy of the soup to avoid modifying the original
        cleaned_soup = BeautifulSoup(str(soup), 'html.parser')

        # Remove head tag and its contents
        if cleaned_soup.head:
            cleaned_soup.head.decompose()

        # List of common selectors for elements to remove
        elements_to_remove = [
            'header', 'footer',           # Standard header and footer tags
            '.header', '.footer',         # Common class names
            '#header', '#footer',         # Common IDs
            'nav', '.nav', '#nav',        # Navigation elements
            '.navigation', '#navigation',
            '.menu', '#menu',
            '.sidebar', '#sidebar',
            '.advertisement', '.ads',     # Advertisement blocks
            '[role="banner"]',            # ARIA roles
            '[role="contentinfo"]',
            '.site-header', '.site-footer',
            '#site-header', '#site-footer',
            'script', 'style',            # Remove script and style tags
            'noscript',                   # Remove noscript tags
            'iframe',                     # Remove iframes
            'meta',                       # Remove meta tags
            'link'                        # Remove link tags
        ]

        # Remove unwanted elements
        for selector in elements_to_remove:
            elements = cleaned_soup.select(selector)
            for element in elements:
                element.decompose()

        # Extract only the body content
        body_content = cleaned_soup.find('body')
        if body_content:
            # Create a new soup with only the body content
            new_soup = BeautifulSoup('<div></div>', 'html.parser')
            new_soup.div.append(body_content)
            return new_soup.div  # Return only the content without html/body tags

        return cleaned_soup  # Return cleaned content if no body tag found

    def minify_html(self, content):
        """Minify HTML content by removing extra whitespace and newlines"""
        if not content:
            return content

        # Convert the BeautifulSoup object to string if needed
        if isinstance(content, BeautifulSoup) or isinstance(content, Tag):
            content = str(content)

        # Remove extra whitespace and newlines
        minified = ' '.join(content.split())

        # Remove spaces between tags
        minified = minified.replace('> <', '><')

        # Remove spaces around tags
        minified = minified.replace(' >', '>')
        minified = minified.replace('< ', '<')

        return minified

    def clean_and_minify_content(self, soup):
        """Clean the content and then minify it"""
        # First clean the content
        cleaned_content = self.clean_content(soup)

        # Then minify it
        minified_content = self.minify_html(cleaned_content)

        # Return as a BeautifulSoup object for consistency
        return BeautifulSoup(minified_content, 'html.parser')

    def fetch_content(self, clean=True, minify=True):
        """
        Fetch and parse the webpage content
        Args:
            clean (bool): Whether to remove header/footer elements
            minify (bool): Whether to minify the HTML content
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()

            # Parse the initial content
            self.soup = BeautifulSoup(response.text, 'html.parser')

            # Clean and minify the content if requested
            if clean:
                if minify:
                    self.soup = self.clean_and_minify_content(self.soup)
                else:
                    self.soup = self.clean_content(self.soup)

                # Try to find and keep only the main content area
                main_content = self.soup.find(['main', 'article', '#content', '.content',
                                             '[role="main"]', '.main-content', '#main-content'])
                if main_content:
                    self.soup = main_content

            return self.soup
        except requests.RequestException as e:
            print(f"Error fetching the webpage: {e}")
            return None

    def get_main_content(self):
        """Extract the main content area of the page"""
        if self.soup is None:
            print("Please fetch the content first using fetch_content()")
            return None

        # List of common selectors for main content
        main_content_selectors = [
            'main',
            'article',
            '#content',
            '.content',
            '[role="main"]',
            '.main-content',
            '#main-content',
            '.post-content',
            '.entry-content',
            '.article-content'
        ]

        # Try each selector
        for selector in main_content_selectors:
            content = self.soup.select_one(selector)
            if content:
                return content

        # If no main content area is found, return the cleaned body
        return self.soup.find('body')

    def get_elements_by_selector(self, selector):
        if self.soup is None:
            print("Please fetch the content first using fetch_content()")
            return []
        return self.soup.select(selector)

    def get_text_from_elements(self, elements):
        return [element.get_text(strip=True) for element in elements]

    def get_nested_text(self, selector):
        elements = self.get_elements_by_selector(selector)
        return self.get_text_from_elements(elements)

    def get_titles_and_links(self, title_selector, link_selector=None):
        title_elements = self.get_elements_by_selector(title_selector)
        results = []

        for title_element in title_elements:
            title = title_element.get_text(strip=True)

            if link_selector:
                link_element = title_element.select_one(link_selector)
            else:
                link_element = title_element if title_element.name == 'a' else title_element.find('a')

            href = link_element['href'] if link_element else None

            # Make sure the href is an absolute URL
            if href and not href.startswith(('http://', 'https://')):
                href = requests.compat.urljoin(self.url, href)

            results.append({'title': title, 'link': href})

        return results

    def save_content_to_file(self, filename='scraped_content.html', clean=True, minify=True):
        """
        Save the content to a file
        Args:
            filename (str): The name of the file to save to
            clean (bool): Whether to save cleaned content
            minify (bool): Whether to minify the content before saving
        """
        if self.soup is None:
            print("Please fetch the content first using fetch_content()")
            return False

        try:
            # Ensure the directory exists
            directory = os.path.dirname(filename)
            if directory:
                os.makedirs(directory, exist_ok=True)

            # Get the content to save
            content = self.get_main_content() if clean else self.soup

            # Minify if requested
            if minify:
                content = self.minify_html(content)

            # Save the content to the file
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(str(content))
            print(f"Content saved to {filename}")
            return True
        except IOError as e:
            print(f"Error saving content to file: {e}")
            return False

# Example usage
if __name__ == "__main__":
    url = "https://example.com"
    scraper = WebScraper(url)

    # Fetch content with cleaning and minification enabled
    content = scraper.fetch_content(clean=True, minify=True)
    if content:
        # Save the cleaned content
        scraper.save_content_to_file('cleaned_content.html')

        # Get text from specific elements
        main_content = scraper.get_main_content()
        if main_content:
            print("Main content found!")
            # Get all paragraph content from main content
            paragraphs = main_content.find_all('p')
            for p in paragraphs:
                print(p.get_text(strip=True))
