from playwright.sync_api import sync_playwright
from pymongo import MongoClient
import time

# ---------------- MongoDB Setup ----------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "pap"
COLLECTION_NAME = "property_urls"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ---------------- Playwright Scraper ----------------
START_URL = "https://www.pap.fr/annonce/vente-appartement-maison-a-partir-du-6-pieces"

def save_url_to_db(url):
    if not collection.find_one({"url": url}):
        collection.insert_one({"url": url})
        print(f"Saved: {url}")
    else:
        print(f"Already exists: {url}")

def scroll_page(page, scroll_pause_time=2, max_scrolls=50):
    last_height = page.evaluate("() => document.body.scrollHeight")
    scrolls = 0
    while scrolls < max_scrolls:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = page.evaluate("() => document.body.scrollHeight")
        if new_height == last_height:
            break  # reached the end
        last_height = new_height
        scrolls += 1
        print(f"Scroll {scrolls} done")

def scrape_property_urls():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(START_URL, timeout=60000)

        # Scroll to load all listings
        scroll_page(page)

        # Extract property URLs using XPath
        # Inspecting site shows links are under <a class="...annonce-link...">
        property_links = page.query_selector_all("//div[@class='item-body']/a")
        print(f"Found {len(property_links)} links on the page")

        for link in property_links:
            url = link.get_attribute("href")
            if url.startswith("/"):
                url = "https://www.pap.fr" + url
            save_url_to_db(url)

        browser.close()

if __name__ == "__main__":
    scrape_property_urls()
