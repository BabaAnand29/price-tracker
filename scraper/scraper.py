from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
from .utils import get_random_user_agent, get_request_headers, random_delay


def scrape_product(url: str) -> dict | None:
    """
    Scrape a single product page using Playwright (handles JS-rendered pages).
    Returns a dict with name, price, availability, and scraped_at timestamp.
    Returns None if scraping fails.

    Target site: books.toscrape.com (a legal, public scraping sandbox).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Create a realistic browser context with custom user-agent and headers
        context = browser.new_context(
            user_agent=get_random_user_agent(),
            extra_http_headers=get_request_headers(),
            viewport={"width": 1280, "height": 720},
        )

        page = context.new_page()

        try:
            # Navigate to the URL
            page.goto(url, timeout=20000, wait_until="networkidle")

            # Wait for main content to appear
            page.wait_for_selector("article.product_page", timeout=10000)

            # Add a random delay to mimic human behaviour
            random_delay(1.0, 3.0)

            # Get the fully rendered HTML
            html = page.content()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # Extract product name
            name_tag = soup.select_one("h1")
            name = name_tag.text.strip() if name_tag else "Unknown"

            # Extract price (books.toscrape.com format)
            price_tag = soup.select_one("p.price_color")
            raw_price = price_tag.text.strip() if price_tag else "0"
            # Remove currency symbols (£, Â, etc.) and convert to float
            price = float("".join(c for c in raw_price if c.isdigit() or c == "."))

            # Extract availability
            avail_tag = soup.select_one("p.availability")
            availability = avail_tag.text.strip() if avail_tag else "Unknown"

            # Extract star rating
            rating_tag = soup.select_one("p.star-rating")
            rating = rating_tag["class"][1] if rating_tag else "Unknown"

            return {
                "name": name,
                "price": price,
                "availability": availability,
                "rating": rating,
                "scraped_at": datetime.utcnow(),
            }

        except Exception as e:
            print(f"[SCRAPER ERROR] Failed to scrape {url}: {e}")
            return None

        finally:
            browser.close()
