import time
from parsel import Selector
from urllib.parse import urljoin
import requests
from pymongo import MongoClient
from settings import BASE_URL, HEADERS, MONGO_URI, MONGO_DB, MONGO_COLLECTION_URL

class Crawler:
    """Crawler for Seven Hills Motorcars — Current and Sold Vehicles"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        # MongoDB setup
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION_URL]

    def parse_item(self):
        """Crawl both current and sold vehicles and store URLs as arrays per category"""

        # Hardcoded categories
        category_urls = [
            urljoin(BASE_URL, "/vehicles"),
            urljoin(BASE_URL, "/vehicles/sold")
        ]
        print(f"Categories to crawl: {category_urls}")

        # Initialize or get single MongoDB document
        doc = self.collection.find_one({"category_url": "vehicles_all"})
        if not doc:
            doc = {"category_url": "vehicles_all", "current": [], "sold": []}

        # Crawl each category
        for category_url in category_urls:
            key_name = "sold" if "sold" in category_url else "current"
            next_page = category_url
            urls = []

            print(f"\n=== Crawling {key_name.upper()} Inventory: {category_url} ===")
            while next_page:
                print(f"Fetching Page: {next_page}")
                resp = self.session.get(next_page, timeout=30)
                if resp.status_code != 200:
                    print(f"Stopping {category_url}: Status {resp.status_code}")
                    break

                sel = Selector(resp.text)
                product_urls = sel.xpath('//div[contains(@class,"sh-vehicle-row")]//a[contains(@class,"sh-inventory-item")]/@href').getall()
                for href in product_urls:
                    full_url = urljoin(BASE_URL, href.strip())
                    urls.append(full_url)
                    print(f"Found Vehicle: {full_url}")
                # Pagination
                next_btn = sel.xpath('//li[contains(@class, "next_page") and not(contains(@class, "disabled"))]/a/@href').get()
                if next_btn and next_btn != "#":
                    next_page = urljoin(BASE_URL, next_btn)
                    time.sleep(1)  # polite delay
                else:
                    next_page = None
                    print("No more pages in this category.")

            # Merge URLs into MongoDB document and remove duplicates
            doc[key_name].extend(urls)
            doc[key_name] = list(set(doc[key_name]))

        # Save final document
        self.collection.update_one(
            {"category_url": "vehicles_all"},
            {"$set": doc},
            upsert=True
        )
        print(f"\nSaved {len(doc['current'])} current and {len(doc['sold'])} sold vehicle URLs.")

    def start(self):
        self.parse_item()

    def close(self):
        self.session.close()
        self.client.close()

if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
