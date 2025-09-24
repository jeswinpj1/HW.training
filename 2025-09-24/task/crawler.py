#WORKING CODE UP .................................................................................................................................


import os
import re
import logging
from urllib.parse import urljoin
from pymongo import MongoClient
import undetected_chromedriver as uc
from lxml import html
import time

# ----------------- Logging Setup -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ----------------- MongoDB Setup -----------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "interspar"
COLLECTION_NAME = "products_nested"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

BASE_URL = "https://www.interspar.at/shop/weinwelt/"

SAVE_DIR = "responses"
os.makedirs(SAVE_DIR, exist_ok=True)

# Limit pages for testing (set None for full scrape)
PAGE_LIMIT = 2


def safe_filename(url: str) -> str:
    """Convert URL into safe filename"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', url)[:100] + ".html"


def save_html(url, page_source):
    """Save page HTML locally for debugging"""
    filename = os.path.join(SAVE_DIR, safe_filename(url))
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page_source)


def fetch(driver, url):
    """Open page in Selenium, return lxml tree"""
    try:
        full_url = urljoin(BASE_URL, url)  # ensure absolute URL
        driver.get(full_url)
        time.sleep(3)  # wait for page load
        page_source = driver.page_source
        save_html(full_url, page_source)
        return html.fromstring(page_source)
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None


def normalize_urls(urls):
    """Convert relative URLs to absolute URLs"""
    return [urljoin(BASE_URL, u) for u in urls]


def get_category_urls(driver):
    tree = fetch(driver, BASE_URL)
    if tree is None:
        return []
    urls = tree.xpath("//ul[contains(@class,'categories__list')]//li[contains(@class,'categories__category')]//a/@href")
    return normalize_urls(urls)


def get_subcategory_urls(driver, category_url):
    tree = fetch(driver, category_url)
    if tree is None:
        return []
    urls = tree.xpath("//ul[contains(@class,'submenu1')]//li[contains(@class,'submenu__item')]//a/@href")
    return normalize_urls(urls)


def get_product_urls(driver, subcategory_url, page_limit=None):
    product_urls = []
    page = 1
    while True:
        if page_limit and page > page_limit:
            break
        url = f"{subcategory_url}?page={page}"
        tree = fetch(driver, url)
        if tree is None:
            break
        products = tree.xpath("//div[contains(@class,'product__top')]//a[contains(@class,'product__titleContainer')]/@href")
        if not products:
            break
        product_urls.extend(normalize_urls(products))
        logging.info(f"      Page {page}: {len(products)} products")
        page += 1
    return product_urls


def main():
    options = uc.ChromeOptions()
    options.headless = False  # set True to run headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)

    try:
        categories = get_category_urls(driver)
        logging.info(f"Found {len(categories)} categories")

        for cat_url in categories:
            logging.info(f"Processing category: {cat_url}")
            subcategories = get_subcategory_urls(driver, cat_url)
            logging.info(f" → {len(subcategories)} subcategories")

            category_doc = {"category": cat_url, "subcategories": []}

            for sub_url in subcategories:
                logging.info(f"   Processing subcategory: {sub_url}")
                products = get_product_urls(driver, sub_url, page_limit=PAGE_LIMIT)
                logging.info(f"   → {len(products)} products")

                sub_doc = {"subcategory": sub_url, "products": products}
                category_doc["subcategories"].append(sub_doc)

            if category_doc["subcategories"]:
                collection.insert_one(category_doc)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()




# 2222222....................................................................

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ pymono product_nested ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  cat_urls 2nd time run !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# import os
# import re
# import logging
# from urllib.parse import urljoin
# from pymongo import MongoClient
# import undetected_chromedriver as uc
# from lxml import html
# import time

# # ----------------- Logging Setup -----------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )

# # ----------------- MongoDB Setup -----------------
# MONGO_URI = "mongodb://localhost:27017/"
# DB_NAME = "interspar"
# COLLECTION_NAME = "cat_urls"

# client = MongoClient(MONGO_URI)
# db = client[DB_NAME]
# collection = db[COLLECTION_NAME]

# BASE_URL = "https://www.interspar.at/shop/weinwelt/"
# SAVE_DIR = "responses"
# os.makedirs(SAVE_DIR, exist_ok=True)

# # Limit pages for testing (set None for full scrape)
# PAGE_LIMIT = 2


# def safe_filename(url: str) -> str:
#     """Convert URL into safe filename"""
#     return re.sub(r'[^a-zA-Z0-9_-]', '_', url)[:100] + ".html"


# def save_html(url, page_source):
#     """Save page HTML locally for debugging"""
#     filename = os.path.join(SAVE_DIR, safe_filename(url))
#     with open(filename, "w", encoding="utf-8") as f:
#         f.write(page_source)


# def fetch(driver, url):
#     """Open page in Selenium, return lxml tree"""
#     try:
#         full_url = urljoin(BASE_URL, url)
#         driver.get(full_url)
#         time.sleep(3)  # wait for page load
#         page_source = driver.page_source
#         save_html(full_url, page_source)
#         return html.fromstring(page_source)
#     except Exception as e:
#         logging.error(f"Failed to fetch {url}: {e}")
#         return None


# def normalize_urls(urls):
#     """Convert relative URLs to absolute URLs"""
#     return [urljoin(BASE_URL, u) for u in urls]


# def get_category_urls(driver):
#     tree = fetch(driver, BASE_URL)
#     if tree is None:
#         return []
#     urls = tree.xpath("//ul[contains(@class,'categories__list')]//li[contains(@class,'categories__category')]//a/@href")
#     return normalize_urls(urls)


# def get_subcategory_urls(driver, category_url):
#     tree = fetch(driver, category_url)
#     if tree is None:
#         return []
#     urls = tree.xpath("//ul[contains(@class,'submenu1')]//li[contains(@class,'submenu__item')]//a/@href")
#     urls = normalize_urls(urls)
#     # skip main category itself to avoid duplicates
#     urls = [u for u in urls if u != category_url]
#     return urls


# def get_product_urls(driver, subcategory_url, page_limit=None):
#     product_urls = []
#     page = 1
#     while True:
#         if page_limit and page > page_limit:
#             break
#         url = f"{subcategory_url}?page={page}"
#         tree = fetch(driver, url)
#         if tree is None:
#             break
#         products = tree.xpath("//div[contains(@class,'product__top')]//a[contains(@class,'product__titleContainer')]/@href")
#         if not products:
#             break
#         product_urls.extend(normalize_urls(products))
#         logging.info(f"      Page {page}: {len(products)} products")
#         page += 1
#     return product_urls


# def main():
#     options = uc.ChromeOptions()
#     options.headless = False  # change True to run headless
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")

#     driver = uc.Chrome(options=options)

#     try:
#         categories = get_category_urls(driver)
#         logging.info(f"Found {len(categories)} categories")

#         for cat_url in categories:
#             logging.info(f"Processing category: {cat_url}")
#             subcategories = get_subcategory_urls(driver, cat_url)
#             logging.info(f" → {len(subcategories)} subcategories")

#             for sub_url in subcategories:
#                 logging.info(f"   Processing subcategory: {sub_url}")
#                 products = get_product_urls(driver, sub_url, page_limit=PAGE_LIMIT)
#                 logging.info(f"   → {len(products)} products")

#                 # Insert immediately for each subcategory
#                 if products:
#                     sub_doc = {
#                         "category": cat_url,
#                         "subcategory": sub_url,
#                         "products": products
#                     }
#                     collection.insert_one(sub_doc)

#     finally:
#         driver.quit()


# if __name__ == "__main__":
#     main()
