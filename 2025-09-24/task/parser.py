# import os
# import re
# import logging
# import time
# from urllib.parse import urljoin
# from pymongo import MongoClient
# import undetected_chromedriver as uc
# from lxml import html

# # ----------------- Logging Setup -----------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )

# # ----------------- MongoDB Setup -----------------
# MONGO_URI = "mongodb://localhost:27017/"
# DB_NAME = "interspar"
# PRODUCTS_COLLECTION = "products_nested"  # your collection with URLs
# DETAILS_COLLECTION = "products_details"  # collection to save product details

# client = MongoClient(MONGO_URI)
# db = client[DB_NAME]
# products_col = db[PRODUCTS_COLLECTION]
# details_col = db[DETAILS_COLLECTION]

# BASE_URL = "https://www.interspar.at/shop/weinwelt/"

# SAVE_DIR = "responses"
# os.makedirs(SAVE_DIR, exist_ok=True)


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
#         time.sleep(3)
#         page_source = driver.page_source
#         save_html(full_url, page_source)
#         return html.fromstring(page_source)
#     except Exception as e:
#         logging.error(f"Failed to fetch {url}: {e}")
#         return None


# def parse_product(tree):
#     """Extract required fields from a product page"""
#     try:
#         title = tree.xpath("//h1[contains(@class,'product-title')]/text()")
#         title = title[0].strip() if title else None

#         price = tree.xpath("//span[contains(@class,'price')]/text()")
#         price = price[0].strip() if price else None

#         country = tree.xpath("//th[contains(text(),'Herkunft')]/following-sibling::td/text()")
#         country = country[0].strip() if country else None

#         manufacturer = tree.xpath("//th[contains(text(),'Hersteller')]/following-sibling::td/text()")
#         manufacturer = manufacturer[0].strip() if manufacturer else None

#         production = tree.xpath("//th[contains(text(),'Produktion')]/following-sibling::td/text()")
#         production = production[0].strip() if production else None

#         description = tree.xpath("//div[contains(@class,'product-description')]//p/text()")
#         description = " ".join([d.strip() for d in description if d.strip()])

#         return {
#             "title": title,
#             "price": price,
#             "country": country,
#             "manufacturer": manufacturer,
#             "production": production,
#             "description": description
#         }
#     except Exception as e:
#         logging.error(f"Error parsing product: {e}")
#         return None


# def main():
#     options = uc.ChromeOptions()
#     options.headless = False  # change to True to run headless
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")

#     driver = uc.Chrome(options=options)

#     try:
#         # Loop through all saved product URLs in MongoDB
#         for category_doc in products_col.find():
#             for subcat in category_doc.get("subcategories", []):
#                 for product_url in subcat.get("products", []):
#                     logging.info(f"Processing product: {product_url}")
#                     tree = fetch(driver, product_url)
#                     if tree is None:
#                         continue
#                     product_data = parse_product(tree)
#                     if product_data:
#                         product_data["url"] = product_url
#                         product_data["category"] = category_doc.get("category")
#                         product_data["subcategory"] = subcat.get("subcategory")
#                         details_col.insert_one(product_data)
#                         logging.info(f"Saved: {product_data['title']}")

#     finally:
#         driver.quit()


# if __name__ == "__main__":
#     main()


#.........................................................................................................................................................




import os
import re
import logging
import time
from urllib.parse import urljoin
from pymongo import MongoClient
import undetected_chromedriver as uc
from lxml import html

# ----------------- Logging Setup -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ----------------- MongoDB Setup -----------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "interspar"
PRODUCTS_COLLECTION = "products_nested"  # collection with URLs
DETAILS_COLLECTION = "products_details"  # collection to save product details

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
products_col = db[PRODUCTS_COLLECTION]
details_col = db[DETAILS_COLLECTION]

BASE_URL = "https://www.interspar.at/shop/weinwelt/"

# SAVE_DIR = "responses"
# os.makedirs(SAVE_DIR, exist_ok=True)


def safe_filename(url: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', url)[:100] + ".html"


# def save_html(url, page_source):
#     filename = os.path.join( safe_filename(url))
#     with open(filename, "w", encoding="utf-8") as f:
#         f.write(page_source)


def fetch(driver, url):
    try:
        full_url = urljoin(BASE_URL, url)
        driver.get(full_url)
        time.sleep(3)
        page_source = driver.page_source
        # save_html(full_url, page_source)
        return html.fromstring(page_source)
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None

def parse_product(tree):
    """Extract detailed product information, return empty strings for missing fields."""
    def extract_text(xpath_expr):
        elements = tree.xpath(xpath_expr)
        text = " ".join([t.strip() for t in elements if t.strip()])
        return text if text else ""  # return empty string instead of None

    try:
        title = extract_text("//h1[contains(@class,'productDetail__title')]//text()")
        taste = extract_text("//h3[contains(@class,'productDetail__taste')]//text()")

        # Price
        price_int = extract_text("//span[contains(@class,'price__int')]/text()")
        price_dec = extract_text("//span[contains(@class,'price__dec')]/text()")
        currency = extract_text("//span[contains(@class,'price__currency')]/text()")
        price = f"{price_int}.{price_dec} {currency}".strip() if price_int else ""
        liter_price = extract_text("//span[contains(@class,'price__liter')]/text()")

        # Country & Volume
        country = extract_text("//span[contains(@class,'product__info--country')]//text() | //p[contains(.,'Land')]/text()")
        volume = extract_text("//span[contains(@class,'product__info--content')]//text()")

        # Art / product code
        art_number = extract_text("//h3[contains(@class,'productDetail__subtitle')]//text()[contains(.,'Art:')]|//p[contains(.,'Art:')]/text()")
        if art_number:
            art_number = art_number.replace("Art:", "").strip()

        # Description
        description = extract_text("//div[contains(@class,'productDescription__box')]//text()")

        tasting_notes = extract_text("//span[contains(@class,'productDescription__par infoAttribute')]//text()")

        # Manufacturer / Age / Alcohol
        manufacturer = extract_text("//p[contains(@class,'productDescription__par-producer')]//text()")
        alcohol = extract_text("//p[contains(.,'Alkohol in vol')]/text()")

        # Shipping info
        shipping_info = extract_text("//h3[contains(@class,'productDetail__subtitle')]//b/a/text()")

        return {
            "title": title,
            "taste": taste,
            "price": price,
            "liter_price": liter_price,
            "country": country,
            "volume": volume,
            "art_number": art_number,
            "description": description,
            "tasting_notes": tasting_notes,
            "manufacturer": manufacturer,
            "alcohol": alcohol,
            "shipping_info": shipping_info
        }

    except Exception as e:
        logging.error(f"Error parsing product: {e}")
        return {
            "title": "",
            "taste": "",
            "price": "",
            "liter_price": "",
            "country": "",
            "volume": "",
            "art_number": "",
            "description": "",
            "tasting_notes": "",
            "manufacturer": "",
            "alcohol": "",
            "shipping_info": ""
        }



# def parse_product(tree):
#     """Extract detailed product information robustly, handling nested tags."""
#     def extract_text(xpath_expr):
#         elements = tree.xpath(xpath_expr)
#         text = " ".join([t.strip() for t in elements if t.strip()])
#         return text if text else None

#     try:
#         title = extract_text("//h1[contains(@class,'productDetail__title')]//text()")
#         taste = extract_text("//h3[contains(@class,'productDetail__taste')]//text()")

#         # Price
#         price_int = extract_text("//span[contains(@class,'price__int')]/text()")
#         price_dec = extract_text("//span[contains(@class,'price__dec')]/text()")
#         currency = extract_text("//span[contains(@class,'price__currency')]/text()")
#         price = f"{price_int}.{price_dec} {currency}" if price_int else None
#         liter_price = extract_text("//span[contains(@class,'price__liter')]/text()")

#         # Country & Volume
#         country = extract_text("//span[contains(@class,'product__info--country')]//text() | //p[contains(.,'Land')]/text()")
#         volume = extract_text("//span[contains(@class,'product__info--content')]//text()")

#         # Art / product code
#         art_number = extract_text("//h3[contains(@class,'productDetail__subtitle')]//text()[contains(.,'Art:')]|//p[contains(.,'Art:')]/text()")
#         if art_number:
#             art_number = art_number.replace("Art:", "").strip()

#         # Description
#         description = extract_text("//dd[contains(@class,'productDescription__par infoAttribute')]/text()")
#         tasting_notes = extract_text("//span[contains(@class,'productDescription__par infoAttribute')]//text()")

#         # Manufacturer / Age / Alcohol
#         manufacturer = extract_text("//p[contains(@class,'productDescription__par-producer')]//text()")
#         alcohol = extract_text("//p[contains(.,'Alkohol in vol')]/text()")

#         # Shipping info
#         shipping_info = extract_text("//h3[contains(@class,'productDetail__subtitle')]//b/a/text()")

#         return {
#             "title": title,
#             "taste": taste,
#             "price": price,
#             "liter_price": liter_price,
#             "country": country,
#             "volume": volume,
#             "art_number": art_number,
#             "description": description,
#             "tasting_notes": tasting_notes,
#             "manufacturer": manufacturer,
#             "alcohol": alcohol,
#             "shipping_info": shipping_info
#         }

#     except Exception as e:
#         logging.error(f"Error parsing product: {e}")
#         return None


def main():
    options = uc.ChromeOptions()
    options.headless = False
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)

    try:
        for category_doc in products_col.find():
            for subcat in category_doc.get("subcategories", []):
                for product_url in subcat.get("products", []):
                    logging.info(f"Processing product: {product_url}")
                    tree = fetch(driver, product_url)
                    if tree is None:
                        continue
                    product_data = parse_product(tree)
                    if product_data:
                        product_data["url"] = product_url
                        product_data["category"] = category_doc.get("category")
                        product_data["subcategory"] = subcat.get("subcategory")
                        details_col.insert_one(product_data)
                        logging.info(f"Saved: {product_data['title']}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
