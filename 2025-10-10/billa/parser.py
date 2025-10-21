import re
import time
import logging
import requests
from pymongo import MongoClient 
from settings import (
    HEADERS_PAGE, MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_ENRICHED_DATA,
    REQUEST_DELAY, GRAMMAGE_REGEX, CLIENT_NAME, STORE_ID, EXTRACTION_DATE
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Mongo Connection
mongo_client = MongoClient(MONGO_URI)
col_enriched = mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_ENRICHED_DATA]

RE_GRAM = re.compile(GRAMMAGE_REGEX, re.IGNORECASE)

class Parser:
    def __init__(self):
        self.headers = HEADERS_PAGE
        self.seen_skus = set()

    def start(self):
        logging.info("Starting Product Parsing...")
        page = 1
        while True:
            products = self.fetch_products(page)
            if not products:
                logging.info("Parsing completed.")
                break

            for product in products:
                self.parse_item(product)

            page += 1
            time.sleep(REQUEST_DELAY)

    def fetch_products(self, page):
        params = {
            "page": page, "pageSize": 50, "storeId": STORE_ID, # Correctly uses STORE_ID from settings
            "sortBy": "relevance",
        }
        try:
            r = requests.get(
                "https://shop.billa.at/api/product-discovery/products",
                headers=self.headers, params=params, timeout=30
            )
            r.raise_for_status()
            return r.json().get("results", [])
        except Exception as e:
            logging.error(f"Failed to fetch page {page}: {e}")
            return []

    def parse_item(self, product):
        if not isinstance(product, dict):
            return

        sku = product.get("sku", "")
        if not sku or sku in self.seen_skus:
            return
        self.seen_skus.add(sku)

        item = {
            "unique_id": sku,
            "product_name": product.get("name", ""),
            "brand": product.get("brand", {}).get("name", ""),
            "pdp_url": f"https://shop.billa.at/produkte/{product.get('slug', '')}",
            "regular_price": str(product.get("price", {}).get("regular", {}).get("value", "")),
            "currency": "EUR",
            "competitor_name": CLIENT_NAME,
            "store_addressid": STORE_ID,
            "extraction_date": EXTRACTION_DATE,
            "competitor_product_key": sku,
        }

        # Image
        images = product.get("images", [])
        if images:
            item["image_url_1"] = images[0]
            item["file_name_1"] = f"{sku}_1.PNG"

        # Breadcrumb
        breadcrumbs = [c.get("name", "") for cats in product.get("parentCategories", []) for c in cats]
        item["breadcrumb"] = " > ".join(breadcrumbs[:7])
        
        #grammage
        full_text = f"{item['product_name']} {product.get('descriptionShort', '')}"
        match = RE_GRAM.search(full_text)
        if match:
            item["grammage_quantity"] = match.group(1).replace(",", ".")
            item["grammage_unit"] = match.group(2).lower()

        # Save to Mongo
        try:
            col_enriched.update_one({"unique_id": sku}, {"$set": item}, upsert=True)
            logging.info(f"Saved: {item['product_name']} | {sku}")
        except Exception as e:
            logging.error(f"Error saving {sku}: {e}")

if __name__ == "__main__":
    Parser().start()