from agent_scrapper import scrapper_articles

def main():
    links = [
        "https://laravel-news.com/blog",
        "https://x.com/enunomaduro",
    ]

    for link in links:
        scrapper_articles(link)

if __name__ == "__main__":
    main()
