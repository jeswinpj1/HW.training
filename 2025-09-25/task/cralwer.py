


import os
import re
import logging
from urllib.parse import urljoin
from pymongo import MongoClient
import undetected_chromedriver as uc
from lxml import html
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------- Logging Setup -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ----------------- MongoDB Setup -----------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "interspar2"
COLLECTION_NAME = "products_urls_nested"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

BASE_URL = "https://www.interspar.at/"

SAVE_DIR = "responses"
os.makedirs(SAVE_DIR, exist_ok=True)

PAGE_LIMIT = 2  # set None for full scrape

def safe_filename(url: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', url)[:100] + ".html"

def save_html(url, page_source):
    filename = os.path.join(SAVE_DIR, safe_filename(url))
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page_source)

def fetch(driver, url):
    try:
        full_url = urljoin(BASE_URL, url)
        driver.get(full_url)
        # Wait until at least one product tile appears
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/p/')]"))
        )
        page_source = driver.page_source
        save_html(full_url, page_source)
        return html.fromstring(page_source)
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None

def normalize_urls(urls):
    # Keep only non-empty strings
    valid_urls = [u for u in urls if isinstance(u, str) and u.strip()]
    return [urljoin(BASE_URL, u) for u in valid_urls]

def scroll_to_load(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_main_categories(driver):
    tree = fetch(driver, BASE_URL)
    if tree is None:
        return []

    # XPath targeting <a> tags with data-type="metaleft"
    urls = tree.xpath("//a[@data-type='metaleft']/@href")
    
    # Optional: normalize URLs if needed
    urls = normalize_urls(urls)
    
    # Skip unwanted URLs (like 'online-shop')
    urls = [u for u in urls if "online-shop" not in u]
    
    return urls
def get_offer_subcategories(driver, category_url):
    tree = fetch(driver, category_url)
    if tree is None:
        return []

    # Collect links from all possible submenu/subcategory patterns
    urls = tree.xpath(
        "//ul[@class='flyoutMenu cf']/li/a/@href"
        " | //li[@class='categories__category j-categoriesCategory']/a/@href"
        " | //ul[contains(@class,'submenu1')]//li[contains(@class,'submenu__item')]//a/@href"
    )
    return normalize_urls(urls)


# def get_offer_subcategories(driver, category_url):
#     tree = fetch(driver, category_url)
#     if tree is None:
#         return []

#     # Find the 'Angebote' <h3> and get the following <ul> links
#     urls = tree.xpath(
#         "//ul[@class='flyoutMenu cf']/li/a/@href | //li[@class='categories__category j-categoriesCategory']/a/@href" )
#     return normalize_urls(urls)


def get_brands(driver, category_url):
    tree = fetch(driver, category_url)
    if tree is None:
        return []
    urls = tree.xpath("//div[contains(@class,'brand__list')]//a/@href")
    return normalize_urls(urls)

def get_product_urls(driver, category_url, page_limit=None):
    product_urls = []
    try:
        driver.get(category_url)

        # Scroll until no new products
        scroll_to_load(driver)

        # Now extract products from the fully rendered page
        tree = html.fromstring(driver.page_source)
        products = tree.xpath("//a[contains(@href,'/p/')]/@href")

        product_urls.extend(normalize_urls(products))
        logging.info(f"      Collected {len(products)} products from {category_url}")

    except Exception as e:
        logging.error(f"Failed to collect products from {category_url}: {e}")

    return product_urls


def main():
    options = uc.ChromeOptions()
    options.headless = False
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)

    try:
        main_cats = get_main_categories(driver)
        logging.info(f"Found {len(main_cats)} main categories")

        for main_url in main_cats:
            logging.info(f"Processing main category: {main_url}")

            subcategories =  get_offer_subcategories(driver, main_url)
            logging.info(f" → {len(subcategories)} subcategories/brands")

            main_doc = {"main_category": main_url, "subcategories": []}

            for sub_url in subcategories:
                logging.info(f"   Processing subcategory/brand: {sub_url}")

                # Try to get further brands if grocery-style
                brands = get_brands(driver, sub_url)
                products = []
                if brands:
                    for b in brands:
                        logging.info(f"     Processing brand: {b}")
                        products.extend(get_product_urls(driver, b, PAGE_LIMIT))
                else:
                    # Home-style: subcategory may have its own products
                    products = get_product_urls(driver, sub_url, PAGE_LIMIT)

                logging.info(f"   → {len(products)} products collected")

                sub_doc = {"subcategory_or_brand": sub_url, "products": products}
                main_doc["subcategories"].append(sub_doc)

            if main_doc["subcategories"]:
                collection.insert_one(main_doc)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
