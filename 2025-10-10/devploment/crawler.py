



# #!/usr/bin/env python3
# """
# Scraper for https://shop.billa.at/kategorie
# - Loops through ?page=1...349
# - Collects all product URLs
# - Avoids duplicates
# - Prints count per page and grand total
# """

# import time
# import logging
# import requests
# from lxml import html
# from urllib.parse import urljoin
# from pymongo import MongoClient

# # ---------------- CONFIG ----------------
# BASE_URL = "https://shop.billa.at/kategorie"
# TOTAL_PAGES = 349
# REQUEST_DELAY = 2
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                   "AppleWebKit/537.36 (KHTML, like Gecko) "
#                   "Chrome/120.0.0.0 Safari/537.36"
# }

# # MongoDB (optional)
# MONGO_URI = "mongodb://localhost:27017"
# MONGO_DB = "billa_scraper12"
# MONGO_COLLECTION = "all_products_urls"

# # ---------------- LOGGING ----------------
# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
# )


# # ---------------- FUNCTIONS ----------------
# def get_tree(url):
#     """Fetch and return parsed HTML tree."""
#     try:
#         res = requests.get(url, headers=HEADERS, timeout=30)
#         if res.status_code == 200:
#             return html.fromstring(res.text)
#         else:
#             logging.warning(f"[{res.status_code}] Failed: {url}")
#     except requests.RequestException as e:
#         logging.error(f"Request failed: {e}")
#     return None


# def extract_product_urls(tree):
#     """Extract product links from a category page."""
#     hrefs = tree.xpath("//a[contains(@class,'ws-product-tile__link')]/@href")
#     return [urljoin(BASE_URL, h) for h in hrefs if h.strip()]


# # ---------------- MAIN ----------------
# def scrape_all_pages():
#     all_products = set()

#     for page_num in range(1, TOTAL_PAGES + 1):
#         url = f"{BASE_URL}?page={page_num}"
#         tree = get_tree(url)
#         if not tree:
#             logging.warning(f"Skipping page {page_num}")
#             continue

#         products = extract_product_urls(tree)
#         if not products:
#             logging.warning(f"No products found on page {page_num}")
#             continue

#         before_count = len(all_products)
#         all_products.update(products)
#         new_count = len(all_products) - before_count

#         logging.info(f" Page {page_num}: {len(products)} products "
#                      f"({new_count} new, total unique: {len(all_products)})")

#         time.sleep(REQUEST_DELAY)

#     logging.info(" Finished scraping.")
#     logging.info(f" Grand total unique product URLs: {len(all_products)}")

#     # Save to MongoDB
#     try:
#         client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
#         db = client[MONGO_DB]
#         collection = db[MONGO_COLLECTION]
#         collection.delete_many({})  # clear previous data
#         collection.insert_one({"total": len(all_products), "urls": list(all_products)})
#         logging.info(f" Saved {len(all_products)} product URLs to MongoDB.")
#     except Exception as e:
#         logging.error(f"MongoDB save failed: {e}")

#     return all_products


# if __name__ == "__main__":
#     scrape_all_pages()







"""
Billa Austria API Scraper
-------------------------
- Fetches products via Billa API
- Parses key fields
- Saves/updates each product individually in MongoDB
- Handles up to 352 pages
"""

import requests
from pymongo import MongoClient
from datetime import datetime
import time

# ---------------- CONFIG ----------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "billa_scraper12"
DATA_COLLECTION = "product_data"

COMPETITOR_NAME = "Billa"
STORE_NAME = "Billa Online"
COUNTRY = "Austria"

BASE_API = "https://shop.billa.at/api/products"
STORE_ID = "00-10"
PAGE_SIZE = 30
TOTAL_PAGES = 352
REQUEST_DELAY = 1.5

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://shop.billa.at/kategorie",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
}

# ---------------- MONGO ----------------
mongo_client = MongoClient(MONGO_URI)
col_data = mongo_client[DB_NAME][DATA_COLLECTION]

# ---------------- FETCH PRODUCTS ----------------
def fetch_products(page=0):
    params = {
        "sortBy": "relevance",
        "storeId": STORE_ID,
        "page": page,
        "pageSize": PAGE_SIZE
    }
    try:
        response = requests.get(BASE_API, headers=HEADERS, params=params, timeout=30)
        if response.status_code != 200:
            print(f"Error {response.status_code} on page {page}")
            return None
        return response.json()
    except Exception as e:
        print(f"Request error on page {page}: {e}")
        return None

# ---------------- PARSE & SAVE ----------------
def parse_and_save(product, mongo_client):
    """
    Parse a single product from Billa API JSON and save to MongoDB.
    """
    unique_id = product.get("sku") or product.get("productId") or ""
    product_name = product.get("name", "")
    
    # Brand
    brand = ""
    if isinstance(product.get("brand"), dict):
        brand = product["brand"].get("name", "")
    
    # Breadcrumbs / Categories
    breadcrumb_levels = [""] * 7
    breadcrumbs = []
    parent_categories = product.get("parentCategories", [])
    if parent_categories and isinstance(parent_categories, list):
        first_level = parent_categories[0] if isinstance(parent_categories[0], list) else parent_categories
        for i, cat in enumerate(first_level[:7]):
            breadcrumb_levels[i] = cat.get("name", "")
            breadcrumbs.append(cat.get("name", ""))
    
    # Price
    price_info = product.get("price", {}).get("regular", {})
    regular_price = price_info.get("value")
    if regular_price is not None:
        regular_price = float(regular_price) / 100 if regular_price > 10 else regular_price
        regular_price = f"{regular_price:.2f}"
    else:
        regular_price = ""
    
    # Images
    images = product.get("images", [])
    if isinstance(images, list) and len(images) > 0:
        if isinstance(images[0], dict):
            image_url_1 = images[0].get("url", "")
        else:
            image_url_1 = images[0]
    else:
        image_url_1 = ""
    file_name_1 = f"{unique_id}_1.PNG" if unique_id else ""
    
    # Other fields
    data = {
        "unique_id": unique_id,
        "competitor_name": COMPETITOR_NAME,
        "store_name": STORE_NAME,
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "product_name": product_name,
        "brand": brand,
        "producthierarchy_level1": breadcrumb_levels[0],
        "producthierarchy_level2": breadcrumb_levels[1],
        "producthierarchy_level3": breadcrumb_levels[2],
        "producthierarchy_level4": breadcrumb_levels[3],
        "producthierarchy_level5": breadcrumb_levels[4],
        "producthierarchy_level6": breadcrumb_levels[5],
        "producthierarchy_level7": breadcrumb_levels[6],
        "regular_price": regular_price,
        "currency": "EUR",
        "breadcrumb": " > ".join(breadcrumbs),
        "pdp_url": f"https://shop.billa.at/produkte/{product.get('slug', '')}",
        "product_description": product.get("descriptionShort", ""),
        "storage_instructions": product.get("storageAndUsageStatements", ""),
        "country_of_origin": product.get("countryOfOrigin", ""),
        "allergens": product.get("nutIngredients", ""),
        "ingredients": product.get("ingredients", ""),
        "image_url_1": image_url_1,
        "file_name_1": file_name_1,
        "netcontent": f"{product.get('amount','')} {product.get('volumeLabelShort','')}".strip()
    }
    
    # Save to MongoDB
    col_data.update_one(
        {"unique_id": unique_id},
        {"$set": data},
        upsert=True
    )
    
    print(f"Parsed & Saved: {product_name} ({unique_id})")
    return data

# ---------------- MAIN LOOP ----------------
page = 0
while page < TOTAL_PAGES:
    result = fetch_products(page)
    
    if not result or "results" not in result or len(result["results"]) == 0:
        print(f"No products or failed on page {page}. Skipping...")
        page += 1
        time.sleep(REQUEST_DELAY)
        continue

    for prod in result["results"]:
        try:
            parse_and_save(prod, mongo_client)
        except Exception as e:
            print(f"Error parsing/saving product {prod.get('name','')} ({prod.get('sku','')}): {e}")

    print(f"Completed page {page}")
    page += 1
    time.sleep(REQUEST_DELAY)

print("Finished scraping all pages.")