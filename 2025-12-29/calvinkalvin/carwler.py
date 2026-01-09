import logging
from parsel import Selector
import requests
from pymongo import MongoClient
from settings import HEADERS, BASE_URL

class Crawler:
    """Calvin Klein Product URL Crawler"""

    def __init__(self):
        # MongoDB connection
        self.mongo = MongoClient("mongodb://localhost:27017")
        self.db = self.mongo["calvinklein"]
        self.collection = self.db["product_urls"]

    def start(self):
        """Start crawling categories"""

        # List of category URLs to crawl
        urls = [
            f"{BASE_URL}/en/women/apparel",
        ]

        for url in urls:
            page = 0
            sz = 16  # items per page
            while True:
                api_url = f"{url}?sz={sz}&start={page}"
                HEADERS['referer'] = url

                response = requests.get(api_url, headers=HEADERS)
                if response.status_code != 200:
                    logging.warning(f"Failed to fetch {api_url}")
                    break

                has_next = self.parse_items(response, url)
                if not has_next:
                    logging.info(f"Pagination finished for {url}")
                    break

                page += sz

    def parse_items(self, response, category_url):
        """Parse product items and save URLs to MongoDB"""

        sel = Selector(response.text)
        product_divs = sel.xpath('//div[@class="tile-body"]/div[@class="pdp-link"]')

        if not product_divs:
            return False

        for product in product_divs:
            url = product.xpath('a[@class="ds-product-name"]/@href').get()
            name = product.xpath('a[@class="ds-product-name"]/span/text()').get()

            if url:
                item = {
                    "product_url": BASE_URL + url,
                    "name": name.strip() if name else "",
                    "category": category_url
                }
                logging.info(item)
                try:
                    self.collection.insert_one(item)
                except Exception as e:
                    logging.warning(f"Failed to insert: {e}")

        return True

    def close(self):
        """Close MongoDB connection"""
        self.mongo.close()


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
