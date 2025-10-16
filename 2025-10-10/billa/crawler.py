
# import logging
# import time
# import re
# import requests
# from lxml import html
# from pymongo import MongoClient
# from datetime import datetime
# from settings import *

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(levelname)s:%(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )

# mongo_client = MongoClient(MONGO_URI)
# col_data = mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_DATA]

# BASE_API = "https://shop.billa.at/api/products"

# class Crawler:
#     def fetch_products(self, page=0):
#         params = {
#             "sortBy": "relevance",
#             "storeId": STORE_ID,
#             "page": page,
#             "pageSize": PAGE_SIZE
#         }
#         try:
#             res = requests.get(BASE_API, headers=HEADERS_PAGE, params=params, timeout=30)
#             if res.status_code != 200:
#                 logging.error(f"Page {page}: Received status {res.status_code}")
#                 return None
#             return res.json()
#         except Exception as e:
#             logging.error(f"Page {page}: Request failed -> {e}")
#             return None

#     def fetch_pdp_grammage(self, pdp_url):
#         """
#         Fetch PDP page and extract quantity/unit from the product information UL.
#         """
#         try:
#             r = requests.get(pdp_url, headers=HEADERS_PAGE, timeout=30)
#             if r.status_code != 200:
#                 return "", ""
#             tree = html.fromstring(r.text)
#             li_texts = tree.xpath(
#                 '//ul[contains(@class,"ws-product-information__piece-description")]//li//text()'
#             )
#             for text in li_texts:
#                 match = re.search(r'(\d+[\.,]?\d*)\s?(g|kg|ml|l|pcs|Stück)', text, re.IGNORECASE)
#                 if match:
#                     qty = match.group(1).replace(",", ".")
#                     unit = match.group(2)
#                     return qty, unit
#             return "", ""
#         except Exception as e:
#             logging.warning(f"PDP fetch failed {pdp_url}: {e}")
#             return "", ""

#     def parse_item(self, product):
#         if not isinstance(product, dict):
#             logging.warning(f"parse_item received non-dict: {product}")
#             return

#         uid = product.get("sku") or ""
#         name = product.get("name") or ""
#         brand = product.get("brand", {}).get("name") if isinstance(product.get("brand"), dict) else ""

#         # Regular price
#         price_val = product.get("price", {}).get("regular", {}).get("value", 0)
#         regular_price = f"{price_val/100:.2f}" if price_val else ""

#         # Selling price if available
#         selling_val = product.get("price", {}).get("selling", {}).get("value", 0)
#         selling_price = f"{selling_val/100:.2f}" if selling_val else ""

#         pdp_url = f"https://shop.billa.at/produkte/{product.get('slug', '')}"
#         grammage_quantity, grammage_unit = self.fetch_pdp_grammage(pdp_url)

#         item = {
#             "unique_id": uid,
#             "product_name": name,
#             "brand": brand,
#             "regular_price": regular_price,
#             "selling_price": selling_price,
#             "currency": "EUR",
#             "grammage_quantity": grammage_quantity,
#             "grammage_unit": grammage_unit,
#             "pdp_url": pdp_url,
#             "competitor_name": CLIENT_NAME,
#             "extraction_date": datetime.now().strftime("%Y-%m-%d"),
#         }

#         try:
#             col_data.update_one({"unique_id": uid}, {"$set": item}, upsert=True)
#             logging.info(f"Saved {item['product_name']}")
#         except Exception as e:
#             logging.error(f"Error saving product {name}: {e}")

#     def start(self):
#         for p in range(TOTAL_PAGES):
#             js = self.fetch_products(p)
#             if not js:
#                 logging.warning(f"Page {p}: No response")
#                 continue

#             results = js.get("results", [])
#             if not isinstance(results, list):
#                 logging.error(f"Page {p}: Unexpected results type: {type(results)}")
#                 continue

#             for prod in results:
#                 try:
#                     if isinstance(prod, dict):
#                         self.parse_item(prod)
#                     else:
#                         logging.warning(f"Skipping non-dict product: {prod}")
#                 except Exception as e:
#                     logging.error(f"Error parsing product {prod}: {e}")

#             logging.info(f"Completed page {p}")
#             time.sleep(REQUEST_DELAY)

# if __name__ == "__main__":
#     Crawler().start()





#>>>>>>>>>>>>>>>>>>>>>>>>................................>>>>>>>>>>>>>>>>>>>>>......................>>>>>>>>>>>>>>>>>>>>>>>>.....................>>>>>>>>>>>>.



import logging
import time
import re
import requests
from lxml import html
from pymongo import MongoClient
from datetime import datetime
from settings import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

mongo_client = MongoClient(MONGO_URI)
col_data = mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_DATA]

BASE_API = "https://shop.billa.at/api/product-discovery/products"

class Crawler:
    def fetch_products(self, page=0):
        params = {
            "page": page,
            "sortBy": "relevance",
            "storeId": STORE_ID,
            "enableStatistics": "false",
            "enablePersonalization": "false",
            "pageSize": PAGE_SIZE
        }
        try:
            res = requests.get(BASE_API, headers=HEADERS_PAGE, params=params, timeout=30)
            if res.status_code != 200:
                logging.error(f"Page {page}: Received status {res.status_code}")
                return None
            return res.json()
        except Exception as e:
            logging.error(f"Page {page}: Request failed -> {e}")
            return None

    def fetch_pdp_grammage(self, pdp_url):
        """Fetch PDP page and extract quantity/unit from UL."""
        try:
            r = requests.get(pdp_url, headers=HEADERS_PAGE, timeout=30)
            if r.status_code != 200:
                return "", ""
            tree = html.fromstring(r.text)
            li_texts = tree.xpath('//ul[contains(@class,"ws-product-information__piece-description")]//li//text()')
            for text in li_texts:
                match = re.search(r'(\d+[\.,]?\d*)\s?(g|kg|ml|l|pcs|Stück)', text, re.IGNORECASE)
                if match:
                    qty = match.group(1).replace(",", ".")
                    unit = match.group(2)
                    return qty, unit
            return "", ""
        except Exception as e:
            logging.warning(f"PDP fetch failed {pdp_url}: {e}")
            return "", ""

    def parse_item(self, product):
        if not isinstance(product, dict):
            logging.warning(f"parse_item received non-dict: {product}")
            return

        uid = product.get("sku") or ""
        name = product.get("name") or ""
        brand = product.get("brand", {}).get("name") if isinstance(product.get("brand"), dict) else ""

        # Regular and selling prices
        regular_val = product.get("price", {}).get("regular", {}).get("value", 0)
        selling_val = product.get("price", {}).get("selling", {}).get("value", 0)
        regular_price = f"{regular_val/100:.2f}" if regular_val else ""
        selling_price = f"{selling_val/100:.2f}" if selling_val else ""

        pdp_url = f"https://shop.billa.at/produkte/{product.get('slug', '')}"
        grammage_quantity, grammage_unit = self.fetch_pdp_grammage(pdp_url)

        item = {
            "unique_id": uid,
            "product_name": name,
            "brand": brand,
            "regular_price": regular_price,
            "selling_price": selling_price,
            "currency": "EUR",
            "grammage_quantity": grammage_quantity,
            "grammage_unit": grammage_unit,
            "pdp_url": pdp_url,
            "store_name": "",
            "competitor_name": CLIENT_NAME,
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        }

        try:
            col_data.update_one({"unique_id": uid}, {"$set": item}, upsert=True)
            logging.info(f"Saved {item['product_name']}")
        except Exception as e:
            logging.error(f"Error saving product {name}: {e}")

    def start(self):
        for p in range(TOTAL_PAGES):
            js = self.fetch_products(p)
            if not js:
                logging.warning(f"Page {p}: No response")
                continue

            results = js.get("results", [])
            if not isinstance(results, list):
                logging.error(f"Page {p}: Unexpected results type: {type(results)}")
                continue

            for prod in results:
                try:
                    self.parse_item(prod)
                except Exception as e:
                    logging.error(f"Error parsing product {prod}: {e}")

            logging.info(f"Completed page {p}")
            time.sleep(REQUEST_DELAY)

if __name__ == "__main__":
    Crawler().start()
