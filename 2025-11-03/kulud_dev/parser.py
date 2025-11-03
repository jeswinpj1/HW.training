import logging
import time
import requests
from parsel import Selector
from pymongo import MongoClient
from urllib.parse import urljoin
from settings import (
    BASE_URL,
    HEADERS_PAGE as HEADERS,
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_CATEGORY,  # where crawler saved product URLs
)

# Target collection for parsed product details
MONGO_COLLECTION_PARSED = "kulud_product_details"
REQUEST_DELAY = 1  # seconds between requests


class Parser:
    """Kulud Product Parser — reads product URLs from DB and parses details"""

    def __init__(self):
        # MongoDB setup
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.source_col = self.db[MONGO_COLLECTION_CATEGORY]   # crawler collection
        self.target_col = self.db[MONGO_COLLECTION_PARSED]    # parsed details

    def start(self):
        """Fetch all product URLs from nested structure in DB and parse"""
        logging.info("Starting Kulud Product Parser...")

        # Fetch all category documents containing subcategories
        docs = self.source_col.find({}, {"subcategories.products": 1})

        urls = []
        for doc in docs:
            for sub in doc.get("subcategories", []):
                urls.extend(sub.get("products", []))

        # Remove duplicates
        urls = list(set(urls))
        logging.info(f"Found {len(urls)} product URLs to parse.")

        for url in urls:
            # Skip if already parsed
            if self.target_col.find_one({"url": url}):
                logging.info(f"Skipping (already parsed): {url}")
                continue

            try:
                response = requests.get(url, headers=HEADERS, timeout=30)
                if response.status_code == 200:
                    self.parse_item(url, response)
                else:
                    logging.warning(f"Failed to fetch {url} [{response.status_code}]")
            except requests.RequestException as e:
                logging.error(f"Request failed for {url}: {e}")

            time.sleep(REQUEST_DELAY)

        logging.info("Parsing completed for all URLs.")


    # -------------------------------------------------------------------------
    def process_category(self, category_url):
        """Handle pagination and extract product URLs from category pages"""
        page_url = category_url
        while page_url:
            try:
                response = requests.get(page_url, headers=HEADERS, timeout=20)
                if response.status_code != 200:
                    logging.warning(f"Failed to fetch category: {page_url}")
                    break

                sel = Selector(text=response.text)
                product_links = sel.xpath('//div[contains(@class,"product-item card")]//a[contains(@class,"product-item__image")]/@href').getall()
                product_links = [urljoin(BASE_URL, href) for href in product_links]

                for product_url in product_links:
                    if not self.target_col.find_one({"url": product_url}):
                        self.process_product(product_url)

                # pagination
                next_page = sel.xpath('//a[@class="pagination__next"]/@href').get()
                if next_page:
                    page_url = urljoin(BASE_URL, next_page)
                    logging.info(f"Next page: {page_url}")
                    time.sleep(REQUEST_DELAY)
                else:
                    page_url = None

            except Exception as e:
                logging.error(f"Error processing category {category_url}: {e}")
                break

    # -------------------------------------------------------------------------
    def process_product(self, url):
        """Download product page and extract details"""
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                self.parse_item(url, response)
            else:
                logging.warning(f"Failed to fetch product {url} [{response.status_code}]")
        except requests.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
        time.sleep(REQUEST_DELAY)

    # -------------------------------------------------------------------------
    def parse_item(self, url, response):
        """Extract and save product details"""
        sel = Selector(text=response.text)

        # --- XPaths ---
        PRODUCT_NAME_XPATH = '//span[@class="product__title"]/text()'
        SALE_PRICE_XPATH = 'normalize-space(//span[@class="price "])'
        MRP_PRICE_XPATH = 'normalize-space(//del[contains(@class,"product-price--compare")])'
        DISCOUNT_XPATH = '//span[contains(@class,"product-item__badge--sale") or contains(@class,"save-text")]/text()'

        # --- Extract values ---
        name = sel.xpath(PRODUCT_NAME_XPATH).get(default="").strip()
        sale_price = sel.xpath(SALE_PRICE_XPATH).get(default="").replace("QR", "").strip()
        mrp_price = sel.xpath(MRP_PRICE_XPATH).get(default="").replace("QR", "").strip()
        discount = sel.xpath(DISCOUNT_XPATH).get(default="").strip()

        # --- Stock status ---
        in_stock_text = sel.xpath('//*[contains(@class,"fa-check-circle")]/following-sibling::text()').get(default="").strip().lower()
        out_stock_text = sel.xpath('//*[contains(@class,"fa-times-circle")]/following-sibling::text()').get(default="").strip().lower()

        if "out of stock" in out_stock_text:
            instock = False
        elif "in stock" in in_stock_text:
            instock = True
        else:
            instock = True  # default fallback

        # --- Price logic ---
        if not mrp_price:
            mrp_price = sale_price or ""

        # Compute discount if missing but price difference exists
        if not discount and mrp_price and sale_price and mrp_price != sale_price:
            try:
                discount_percent = (1 - (float(sale_price) / float(mrp_price))) * 100
                discount = f"{discount_percent:.0f}% OFF"
            except ValueError:
                discount = ""

        # --- Build item ---
        item = {
            "url": url,
            "product_name": name,
            "mrp": mrp_price,
            "sale_price": sale_price,
            "discount": discount,
            "instock": instock,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        logging.info(f"Extracted: {item}")

        # --- Save ---
        try:
            self.target_col.insert_one(item)
            logging.info(f"Saved: {url}")
        except Exception as e:
            logging.error(f"Failed to insert {url}: {e}")


    # -------------------------------------------------------------------------
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        logging.info("MongoDB connection closed.")


# -------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    parser = Parser()
    parser.start()
    parser.close()


# ..........................................................................

# import logging
# import time
# import requests
# from parsel import Selector
# from pymongo import MongoClient
# from settings import (
#     HEADERS_PAGE as HEADERS,
#     MONGO_URI,
#     MONGO_DB_NAME,
#     MONGO_COLLECTION_PRODUCT,
# )

# class Parser:
#     """Kulud Product Parser"""

#     def __init__(self):
#         # Mongo connection
#         self.client = MongoClient(MONGO_URI)
#         self.db = self.client[MONGO_DB_NAME]
#         self.col = self.db[MONGO_COLLECTION_PRODUCT]

#     def start(self):
#         """Start parsing products"""

#         metas = [
#             {"url": "https://kuludonline.com/collections/skin-treatment-mouth-ulcer/products/vilco-saliphur-soap-75g"},
#         ]

#         for meta in metas:
#             url = meta.get("url")
#             logging.info(f"Fetching product: {url}")
#             response = requests.get(url, headers=HEADERS, timeout=20)
#             if response.status_code == 200:
#                 self.parse_item(url, response)
#             else:
#                 logging.warning(f"Failed to fetch {url} [{response.status_code}]")

#             time.sleep(1)

#     def parse_item(self, url, response):
#         """Extract product details"""

#         sel = Selector(text=response.text)

#         # ---------------- XPaths ----------------
#         PRODUCT_NAME_XPATH = '//span[@class="product__title"]/text()'
#         SALE_PRICE_XPATH = '//span[@class="price "]/text()'
#         MRP_PRICE_XPATH = '//del[contains(@class,"product-price--compare")]/text()'
#         DISCOUNT_XPATH = '//span[contains(@class,"product-item__badge--sale") or contains(@class,"save-text")]/text()'
#         STOCK_XPATH = '//*[contains(text(), "In stock") and contains(text(), "Out of stock")]/text()'

#         # ---------------- Extract ----------------
#         name = sel.xpath(PRODUCT_NAME_XPATH).get(default="").strip()
#         sale_price = sel.xpath(SALE_PRICE_XPATH).get(default="").replace("QR", "").strip()
#         mrp_price = sel.xpath(MRP_PRICE_XPATH).get(default="").replace("QR", "").strip()
#         discount = sel.xpath(DISCOUNT_XPATH).get(default="").strip()
#         stock_text = sel.xpath(STOCK_XPATH).get(default="").strip()

#         # ---------------- Logic ----------------
#         if not mrp_price:
#             mrp_price = sale_price  # fallback

#         instock = not ("out" in stock_text.lower()) if stock_text else True

#         if not discount and mrp_price and sale_price and mrp_price != sale_price:
#             try:
#                 discount_percent = (1 - (float(sale_price) / float(mrp_price))) * 100
#                 discount = f"{discount_percent:.0f}% OFF"
#             except ValueError:
#                 discount = ""

#         # ---------------- Item ----------------
#         item = {
#             "url": url,
#             "product_name": name,
#             "mrp": mrp_price,
#             "sale_price": sale_price,
#             "discount": discount,
#             "instock": instock,
#         }

#         logging.info(f"Extracted item: {item}")

#         # ---------------- Save to Mongo ----------------
#         try:
#             self.col.insert_one(item)
#             logging.info(f" Saved product: {url}")
#         except Exception as e:
#             logging.error(f" Failed to insert {url}: {e}")

#     def close(self):
#         """Close MongoDB connection"""
#         self.client.close()
#         logging.info("MongoDB connection closed.")


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
#     parser_obj = Parser()
#     parser_obj.start()
#     parser_obj.close()
