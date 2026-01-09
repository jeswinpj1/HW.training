import logging
import requests
from parsel import Selector
from pymongo import MongoClient
from urllib.parse import urljoin

from settings import MONGO_COLLECTION_CATEGORY, MONGO_DB

# ----------------------------
# SETTINGS
# ----------------------------
BASE_URL = "https://eu.targus.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
}


class Crawler:

    # ----------------------------
    # INIT
    # ----------------------------
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.mongo = self.client[MONGO_DB]

    # ----------------------------
    # START
    # ----------------------------
    def start(self):
        start_url = f"{BASE_URL}/collections/all"

        response = requests.get(start_url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            logging.error(f"Failed: {start_url}")
            return

        sel = Selector(response.text)

        # YOUR LOGIC (XPath only)
        urls = sel.xpath('//a[@class="grandchildlink"]/@href').getall()
        logging.info(f"Found: {len(urls)}")

        # absolute + dedupe
        final_urls = []
        for u in urls:
            full_url = urljoin(BASE_URL, u)
            if full_url not in final_urls:
                final_urls.append(full_url)

        self.parse_items(final_urls, start_url)

    # ----------------------------
    # PARSE ITEMS
    # ----------------------------
    def parse_items(self, urls, category_url):
        for product_url in urls:
            item = {
                "product_url": product_url,
                "category": category_url,
                "source": "xpath",
            }

            logging.info(item)

            try:
                self.mongo[MONGO_COLLECTION_CATEGORY].insert_one(item)
            except Exception as e:
                logging.error(e)

    # ----------------------------
    # CLOSE
    # ----------------------------
    def close(self):
        self.client.close()


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    crawler = Crawler()
    crawler.start()
    crawler.close()
