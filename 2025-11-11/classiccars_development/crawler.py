import logging
import time
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import HEADERS, COOKIES, MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_URLS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")

class ClassicCarsCrawler:
    """Crawler to fetch classic car listing URLs and save to MongoDB."""

    BASE_URL = "https://classiccars.com/listings/find/until-1990"
    MAX_PAGES = 600

    def __init__(self):
        # MongoDB connection
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db[MONGO_COLLECTION_URLS]

        # HTTP session
        self.session = requests.Session()

    def start(self):
        """Start crawling pages."""
        page = 1

        while page <= self.MAX_PAGES:
            url = f"{self.BASE_URL}?p={page}"
            logging.info(f"Fetching page {page}...")
            response = self.session.get(url, headers=HEADERS, cookies=COOKIES, timeout=20)

            if response.status_code != 200:
                logging.warning(f"Failed to fetch page {page}, status code: {response.status_code}")
                break

            has_links = self.parse_page(response)
            if not has_links:
                logging.info("No more listings found, stopping.")
                break

            page += 1
            time.sleep(0.5)  # polite delay

    def parse_page(self, response):
        """Extract car listing URLs and save to MongoDB."""
        sel = Selector(response.text)
        links = sel.xpath('//a[@class="d-block w100 dark-link"]/@href').getall()

        if not links[:3]:
            return False

        for link in links:
            full_url = f"https://classiccars.com{link}"
            item = {"url": full_url}
            try:
                self.collection.update_one({"url": full_url}, {"$set": item}, upsert=True)
                logging.info(f"Saved URL: {full_url}")
            except Exception as e:
                logging.warning(f"Failed to save URL {full_url}: {e}")

        return True

    def close(self):
        """Close MongoDB connection."""
        self.client.close()
        logging.info("Crawler closed.")


if __name__ == "__main__":
    crawler = ClassicCarsCrawler()
    crawler.start()
    crawler.close()
