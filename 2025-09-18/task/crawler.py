from __future__ import annotations
import time
import json
import logging
from typing import List, Dict
from urllib.parse import urljoin
from pymongo import MongoClient, errors
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

# ---------------- CONFIG ----------------
BASE_URL = 'https://bahrainfinder.bh/en/'
REQUEST_TIMEOUT = 15000  # ms
SLEEP_BETWEEN_REQUESTS = 1

# MongoDB config
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'bahrainfinder'
COLLECTION_NAME = 'main_urls'

# Output files
OUT_JSON = 'bahrainfinder_products.json'
OUT_JSONL = 'bahrainfinder_products.jsonl'

# Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger('bahrainfinder_scraper')

# ---------------- Helpers ----------------
def dedup_urls(base: str, urls: List[str]) -> List[str]:
    abs_urls = [urljoin(base, u) for u in urls if u]
    return sorted(set(abs_urls))

def save_to_mongo(docs: List[Dict]):
    if not docs:
        return
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        coll = db[COLLECTION_NAME]
        for d in docs:
            try:
                coll.update_one({'url': d['url']}, {'$set': d}, upsert=True)
            except errors.PyMongoError as e:
                logger.warning(f"Failed to save {d['url']}: {e}")
        logger.info(f"Saved {len(docs)} URLs to MongoDB")
    except Exception as e:
        logger.error(f"MongoDB error: {e}")

def export_json_files(docs: List[Dict]):
    try:
        with open(OUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
        with open(OUT_JSONL, 'w', encoding='utf-8') as f:
            for d in docs:
                f.write(json.dumps(d, ensure_ascii=False) + '\n')
        logger.info(f"Exported {len(docs)} URLs to JSON and JSONL")
    except Exception as e:
        logger.error(f"File export error: {e}")

# ---------------- Playwright Scraper ----------------
def get_categories(page: Page) -> List[str]:
    """Fetch main categories using Playwright + XPath."""
    page.goto(BASE_URL, timeout=REQUEST_TIMEOUT,wait_until='domcontentloaded')  # Ensure page is loade
    time.sleep(SLEEP_BETWEEN_REQUESTS)
    nodes = page.query_selector_all('//a[contains(@class,"nav-link")]')
    print("Category Nodes:",nodes)     
    hrefs = [n.get_attribute('href') for n in nodes[:4] if n.get_attribute('href')]
    return dedup_urls(BASE_URL, hrefs)  
       
def get_products(page: Page, cat_url: str) -> List[str]:
    """Fetch all product URLs from a category page including pagination"""
    collected = []
    to_visit = [cat_url]
    visited = set()

    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            page.goto(url, timeout=REQUEST_TIMEOUT)
            time.sleep(SLEEP_BETWEEN_REQUESTS)
        except PlaywrightTimeoutError:
            logger.warning(f"Timeout fetching {url}")
            continue

        # Product links
        nodes = page.query_selector_all('//div[contains(@class,"listing-thumb")]/a')
        hrefs = [n.get_attribute('href') for n in nodes if n.get_attribute('href')]
        collected.extend(dedup_urls(url, hrefs))

        # Pagination links
        next_pages = page.query_selector_all('//a[contains(@aria-label,"Next")]')
        for np in next_pages:
            np_href = np.get_attribute('href')
            if np_href:
                abs_np = urljoin(url, np_href)
                if abs_np not in visited and abs_np not in to_visit:
                    to_visit.append(abs_np)

    return sorted(set(collected))

# ---------------- Main ----------------
def main():
    logger.info("Starting BahrainFinder scraper")
    products_data = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        categories = get_categories(page)

        for cat in categories:
            logger.info(f"Category: {cat}")
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            products = get_products(page, cat)
            logger.info(f"  Found {len(products)} products in {cat}")

            for prod in products:
                products_data.append({
                    "url": prod,
                    "category": cat,
                    "scraped_at": time.strftime('%Y-%m-%d %H:%M:%S')
                })

        browser.close()

    save_to_mongo(products_data)
    export_json_files(products_data)
    logger.info("Done.")

if __name__ == "__main__":
    main()
