import logging
import time
import re
import requests
from parsel import Selector
from pymongo import MongoClient
from datetime import datetime
from settings import (
    API_URL, HEADERS_PAGE, MONGO_URI, MONGO_DB_NAME,
    MONGO_COLLECTION_DATA, PAGE_SIZE, TOTAL_PAGES,
    STORE_ID, CLIENT_NAME, REQUEST_DELAY, GRAMMAGE_REGEX
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

class Crawler:
    def __init__(self):
        self.mongo = MongoClient(MONGO_URI)[MONGO_DB_NAME][MONGO_COLLECTION_DATA]

    def start(self):
        for page in range(TOTAL_PAGES):
            logging.info(f"Fetching page {page}")
            data = self.fetch_products(page)

            if not data:
                logging.warning(f"No products found on page {page}")
                continue

            for product in data.get("results", []):
                self.parse_item(product)

            time.sleep(REQUEST_DELAY)

    def fetch_products(self, page):
        params = {
            "page": page,
            "sortBy": "relevance",
            "storeId": STORE_ID,
            "enableStatistics": "false",
            "enablePersonalization": "false",
            "pageSize": PAGE_SIZE
        }
        try:
            r = requests.get(API_URL, headers=HEADERS_PAGE, params=params, timeout=30)
            return r.json() if r.status_code == 200 else None
        except Exception as e:
            logging.error(f"Error fetching API page {page}: {e}")
            return None

    def parse_item(self, product):
        if not isinstance(product, dict):
            return

        sku = product.get("sku", "")
        pdp_url = f"https://shop.billa.at/produkte/{product.get('slug', '')}"

        reg_val = product.get("price", {}).get("regular", {}).get("value", 0)
        sell_val = product.get("price", {}).get("selling", {}).get("value", 0)

        grammage_qty = ""
        grammage_unit = ""

        try:
            response = requests.get(pdp_url, headers=HEADERS_PAGE, timeout=30)
            if response.status_code == 200:
                sel = Selector(response.text)
                details = sel.xpath('//ul[contains(@class,"ws-product-information__piece-description")]//li/text()').getall()
                for text in details:
                    match = re.search(GRAMMAGE_REGEX, text, re.IGNORECASE)
                    if match:
                        grammage_qty = match.group(1).replace(",", ".")
                        grammage_unit = match.group(2)
                        break
        except Exception:
            pass

        item = {
            "unique_id": sku,
            "product_name": product.get("name", ""),
            "brand": product.get("brand", {}).get("name", ""),
            "regular_price": f"{reg_val/100:.2f}" if reg_val else "",
            "selling_price": f"{sell_val/100:.2f}" if sell_val else "",
            "currency": "EUR",
            "grammage_quantity": grammage_qty,
            "grammage_unit": grammage_unit,
            "pdp_url": pdp_url,
            "competitor_name": CLIENT_NAME,
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        }

        try:
            self.mongo.update_one({"unique_id": sku}, {"$set": item}, upsert=True)
            logging.info(f"Saved: {item['product_name']}")
        except Exception as e:
            logging.error(f"Error saving: {item['product_name']}, {e}")

    def close(self):
        try:
            self.mongo.database.client.close()
        except:
            pass

if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
