"""
scraper.py
----------
Uses newspaper3k to download and parse full article text from any news URL.
"""

from newspaper import Article
from newspaper.article import ArticleException


def scrape_article(url: str) -> dict:
    """
    Downloads and parses a news article from the given URL.

    Returns:
        dict with keys:
            - title  (str)
            - text   (str)
            - authors (list[str])
            - publish_date (str | None)
            - top_image (str | None)

    Raises:
        ValueError  if the URL cannot be fetched or parsed.
    """
    try:
        from newspaper import Config
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        config.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
        }
        article = Article(url, config=config)
        article.download()
        article.parse()
    except ArticleException as e:
        raise ValueError(f"newspaper3k could not parse the article: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error while scraping: {e}")

    if not article.text.strip():
        raise ValueError(
            "The article body is empty. The URL may be behind a paywall or "
            "require JavaScript to render."
        )

    return {
        "title": article.title or "Untitled",
        "text": article.text,
        "authors": article.authors,
        "publish_date": str(article.publish_date) if article.publish_date else None,
        "top_image": article.top_image or None,
    }
