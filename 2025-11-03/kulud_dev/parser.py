import logging
import time
import requests
import item 
from parsel import Selector
from pymongo import MongoClient
from settings import (
    HEADERS_PAGE as HEADERS,
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_CATEGORY,
)

MONGO_COLLECTION_PARSED = "1kulud_product_details1"
REQUEST_DELAY = 1  # seconds between requests


class Parser:
    """Kulud Product Parser — simplified, stable version"""

    def __init__(self):
        # MongoDB setup
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.source_col = self.db[MONGO_COLLECTION_CATEGORY]
        self.target_col = self.db[MONGO_COLLECTION_PARSED]

    def start(self):
        """Fetch product URLs from DB and parse"""
        logging.info("Starting Kulud Product Parser...")

        # Get product URLs from nested structure
        urls = set()
        for doc in self.source_col.find({}, {"subcategories.products": 1}):
            for sub in doc.get("subcategories", []):
                urls.update(sub.get("products", []))

        logging.info(f"Found {len(urls)} product URLs to parse.")

        for url in urls:
            if self.target_col.find_one({"url": url}):
                logging.info(f"Skipping (already parsed): {url}")
                continue

            html = self.get_html(url)
            if html:
                self.parse_item(url, html)
            time.sleep(REQUEST_DELAY)

        logging.info("Parsing completed for all URLs.")

    def get_html(self, url):
        """Fetch product page HTML with retry"""
        for _ in range(3):
            try:
                res = requests.get(url, headers=HEADERS, timeout=20)
                if res.status_code == 200:
                    return res.text
                logging.warning(f"Failed {url} [{res.status_code}]")
            except requests.RequestException as e:
                logging.error(f"Error fetching {url}: {e}")
            time.sleep(1)
        return None

    def parse_item(self, url, html):
        """Extract product details and save"""
        sel = Selector(text=html)

        # --- Extract data ---
        name = sel.xpath('//span[@class="product__title"]/text()').get(default="").strip()
        sale_price = sel.xpath('normalize-space(//span[@class="price "])').get(default="").replace("QR", "").strip()
        mrp_price = sel.xpath('normalize-space(//del[contains(@class,"product-price--compare")])').get(default="").replace("QR", "").strip()
        discount = sel.xpath('//span[contains(@class,"product-item__badge--sale") or contains(@class,"save-text")]/text()').get(default="").strip()

        # Stock check
        in_stock = sel.xpath('//*[contains(@class,"fa-check-circle")]/following-sibling::text()').get(default="").lower()
        out_stock = sel.xpath('//*[contains(@class,"fa-times-circle")]/following-sibling::text()').get(default="").lower()
        instock = False if "out of stock" in out_stock else ("in stock" in in_stock or True)

        # Handle price and discount
        if not mrp_price:
            mrp_price = sale_price
        if not discount and mrp_price and sale_price and mrp_price != sale_price:
            try:
                diff = (1 - float(sale_price) / float(mrp_price)) * 100
                discount = f"{diff:.0f}% OFF"
            except ValueError:
                discount = ""

        item = {
            "url": url,
            "product_name": name,
            "mrp": mrp_price,
            "sale_price": sale_price,
            "discount": discount,
            "instock": instock,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Save item if valid
        if all([item.get("product_name"), item.get("sale_price")]):
            try:
                float(item["sale_price"])
                float(item.get("mrp", 0))
                self.target_col.insert_one(item)
                logging.info(f" Saved: {item['product_name']} — {url}")
            except (ValueError, Exception) as e:
                logging.error(f" Failed to save {url}: {e}")
        else:
            logging.warning(f" Skipped invalid item: {url}")

    def close(self):
            """Close MongoDB connection"""
            self.client.close()
            logging.info("MongoDB connection closed.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    parser = Parser()
    parser.start()
    parser.close()
