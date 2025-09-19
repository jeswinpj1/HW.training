# from __future__ import annotations
# import time
# import json
# import logging
# from typing import Dict, List
# from pymongo import MongoClient, errors
# from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

# # ---------------- CONFIG ----------------
# REQUEST_TIMEOUT = 20000
# SLEEP_BETWEEN_REQUESTS = 1

# # Input file from first crawler
# INPUT_JSON = 'bahrainfinder_products.json'

# # Output
# OUT_JSON = 'bahrainfinder_product_details.json'
# OUT_JSONL = 'bahrainfinder_product_details.jsonl'

# # MongoDB
# MONGO_URI = 'mongodb://localhost:27017/'
# DB_NAME = 'bahrainfinder'
# COLLECTION_NAME = 'products_details'

# # Logging
# logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
# logger = logging.getLogger("bahrainfinder_parser")

# # ---------------- Helpers ----------------
# def save_to_mongo(docs: List[Dict]):
#     if not docs:
#         return
#     try:
#         client = MongoClient(MONGO_URI)
#         db = client[DB_NAME]
#         coll = db[COLLECTION_NAME]
#         for d in docs:
#             try:
#                 coll.update_one({'url': d['url']}, {'$set': d}, upsert=True)
#             except errors.PyMongoError as e:
#                 logger.warning(f"Failed to save {d['url']}: {e}")
#         logger.info(f"Saved {len(docs)} docs to MongoDB")
#     except Exception as e:
#         logger.error(f"MongoDB error: {e}")

# def export_json_files(docs: List[Dict]):
#     try:
#         with open(OUT_JSON, 'w', encoding='utf-8') as f:
#             json.dump(docs, f, ensure_ascii=False, indent=2)
#         with open(OUT_JSONL, 'w', encoding='utf-8') as f:
#             for d in docs:
#                 f.write(json.dumps(d, ensure_ascii=False) + '\n')
#         logger.info(f"Exported {len(docs)} docs to JSON and JSONL")
#     except Exception as e:
#         logger.error(f"File export error: {e}")

# # ---------------- Product Parser ----------------
# def parse_product(page: Page, url: str, category: str) -> Dict:
#     """Extract details from product page"""
#     try:
#         page.goto(url, timeout=REQUEST_TIMEOUT, wait_until="domcontentloaded")
#         time.sleep(SLEEP_BETWEEN_REQUESTS)
#     except PlaywrightTimeoutError:
#         logger.warning(f"Timeout fetching {url}")
#         return {}

#     def text_or_none(xpath):
#         el = page.query_selector(xpath)
#         return el.inner_text().strip() if el else None

#     def all_texts(xpath):
#         els = page.query_selector_all(xpath)
#         return [e.inner_text().strip() for e in els if e.inner_text()]

#     data = {
#         "url": url,
#         "category": category,
#         "reference_number": text_or_none('//span[contains(text(),"Reference Number")]/following-sibling::span'),
#         "broker_display_name": text_or_none('//div[contains(@class,"broker-name")]'),
#         "broker": text_or_none('//div[contains(@class,"broker-info")]'),
#         "category_url": category,
#         "title": text_or_none('//h1'),
#         "description": text_or_none('//div[contains(@class,"description")]'),
#         "location": text_or_none('//span[contains(@class,"location")]'),
#         "price": text_or_none('//span[contains(@class,"price")]'),
#         "currency": text_or_none('//span[contains(@class,"currency")]'),
#         "price_per": text_or_none('//span[contains(@class,"price-per")]'),
#         "bedrooms": text_or_none('//span[contains(text(),"Bedrooms")]/following-sibling::span'),
#         "bathrooms": text_or_none('//span[contains(text(),"Bathrooms")]/following-sibling::span'),
#         "furnished": text_or_none('//span[contains(text(),"Furnished")]/following-sibling::span'),
#         "rera_permit_number": text_or_none('//span[contains(text(),"RERA Permit")]/following-sibling::span'),
#         "dtcm_licence": text_or_none('//span[contains(text(),"DTCM Licence")]/following-sibling::span'),
#         "amenities": all_texts('//ul[contains(@class,"amenities")]/li'),
#         "scraped_ts": time.strftime('%Y-%m-%d %H:%M:%S')
#     }

#     return {k: v for k, v in data.items() if v}

# # ---------------- Main ----------------
# def main():
#     logger.info("Starting BahrainFinder product parser")

#     # Load product URLs from JSON
#     with open(INPUT_JSON, 'r', encoding='utf-8') as f:
#         urls_data = json.load(f)

#     products_data = []

#     with sync_playwright() as pw:
#         browser = pw.chromium.launch(headless=False)
#         page = browser.new_page()

#         for entry in urls_data:
#             url = entry["url"]
#             cat = entry.get("category")
#             logger.info(f"Parsing {url}")
#             product = parse_product(page, url, cat)
#             if product:
#                 products_data.append(product)

#         browser.close()

#     save_to_mongo(products_data)
#     export_json_files(products_data)
#     logger.info("Done parsing products.")

# if __name__ == "__main__":
#     main()



# the main working crawler code 
#............................................................................................................................................................

import time
import json
import logging
from pymongo import MongoClient
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------- CONFIG ----------------
REQUEST_TIMEOUT = 15000
SLEEP_BETWEEN_REQUESTS = 1
INPUT_JSON = "bahrainfinder_products.json"
OUT_JSON = "bahrainfinder_product_details1.jsonl"  # use JSONL for one-by-one
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "bahrainfinder"
COLLECTION_NAME = "product_details1"

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("bahrainfinder_parser")


def save_to_mongo(data: dict):
    """Insert/Update one product in MongoDB"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        coll = db[COLLECTION_NAME]
        coll.update_one({"url": data["url"]}, {"$set": data}, upsert=True)
    except Exception as e:
        logger.error(f"MongoDB insert error for {data.get('url')}: {e}")


def save_to_jsonl(data: dict):
    """Append one product into JSONL file"""
    with open(OUT_JSON, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def parse_product(page, url: str, category: str) -> dict:
    try:
        page.goto(url, timeout=REQUEST_TIMEOUT, wait_until="domcontentloaded")
        time.sleep(SLEEP_BETWEEN_REQUESTS)
    except PlaywrightTimeoutError:
        logger.warning(f"Timeout fetching {url}")
        return {}

    def text_or_none(xpath):
        el = page.query_selector(xpath)
        return el.inner_text().strip() if el else ""

    def attr_or_none(xpath, attr):
        el = page.query_selector(xpath)
        return el.get_attribute(attr).strip() if el else ""

    def all_texts(xpath):
        texts = [e.inner_text().strip() for e in page.query_selector_all(xpath) if e.inner_text()]
        return texts if texts else []

    # --- Property data ---
    data = {
        "url": url,
        "category": category,
        "title": text_or_none('//h1'),
        "description": text_or_none('//div[@id="property-description-excerpt"] | //div[@id="property-description-toggle"]'),
        "reference_number": text_or_none('//ul/li[@id="bf-id"]/strong'),
        "property_usage": text_or_none('//ul/li[@id="usage"]/strong'),
        "price": text_or_none(page, '//ul[contains(@class,"price-wrap-hide-on")]/span/strong'),
        "currency": "BHD",
        # --- Agent details ---
        "broker_display_name": text_or_none('//div[@class="agent-details"]//li[@class="agent-name"]'),
        "broker": text_or_none('//div[@class="agent-details"]//li[@class="agent-list-position"]/a'),
        "broker_profile_url": attr_or_none('//div[@class="agent-details"]//div[@class="agent-image"]/a', "href"),
        
        # --- Furnished info ---
        "furnished": text_or_none('//ul/li[contains(.,"Furnished")]/strong'),

        # --- Amenities list ---
        "amenities": all_texts('//ul[contains(@class,"amenities")]/li'),

        # --- Contact details ---
        "whatsapp": attr_or_none('//a[@id="cta-whatsapp"]', "href"),
        "phone": text_or_none('//a[@id="cta-call"]//span[@class="show-on-click"]'),

        # --- Updated on ---
        "updated_on": text_or_none('//span[contains(@class,"update-on-text")]'),

        # --- Timestamp ---
        "scraped_ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    return data

    return {k: v for k, v in data.items() if v}

def main():
    logger.info("Starting BahrainFinder incremental parser")

    try:
        with open(INPUT_JSON, "r", encoding="utf-8") as f:
            products = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read {INPUT_JSON}: {e}")
        return

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()

        for idx, prod in enumerate(products, 1):
            url = prod["url"]
            category = prod.get("category", "")

            logger.info(f"[{idx}/{len(products)}] Scraping: {url}")
            details = parse_product(page, url, category)

            if details:
                # Show in console
                print(json.dumps(details, indent=2, ensure_ascii=False))

                # Save immediately
                save_to_mongo(details)
                save_to_jsonl(details)

        browser.close()

    logger.info("Done.")


if __name__ == "__main__":
    main()
#.....................................................................................................................................................................