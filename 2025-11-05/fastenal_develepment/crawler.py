import time
import logging
import requests
from urllib.parse import quote
from pymongo import MongoClient
from settings import headers, cookies, API_URL, MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_PRODUCTS

REQUEST_DELAY = 0.5

class Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.categories_collection = self.db[MONGO_COLLECTION_CATEGORY]
        self.products_collection = self.db[MONGO_COLLECTION_PRODUCTS]
    def fetch_products_for_category(self, level_one, level_two, level_three, category_id):
        page_url = f"/product/{quote(level_one)}/{quote(level_two)}/{quote(level_three)}"
        page = 1
        total_pages = 1
        while page <= total_pages:
            payload = {
                "categoryLevelOne": level_one,
                "categoryLevelTwo": level_two,
                "categoryLevelThree": level_three,
                "ignoreCounterBook": True,
                "categoryId": category_id,
                "productListOnly": True,
                "attributeFilters": {},
                "pageUrl": page_url,
                "page": page,
            }
            response = self.session.post(API_URL, headers=headers, cookies=cookies, json=payload, timeout=30)
            if response.status_code != 200:
                logging.warning(f"{level_three} | Page {page} | HTTP {response.status_code}")
                page += 1
                continue
            data = response.json()
            total_pages = data.get("paging", {}).get("totalPages", 1)
            products = data.get("productList", [])
            for prod in products:
                record = {
                    "categoryLevelOne": level_one,
                    "categoryLevelTwo": level_two,
                    "categoryLevelThree": level_three,
                    "categoryId": category_id,
                    "sku": prod.get("sku"),
                    "Company Name": prod.get("brNm", "FASTENAL"),
                    "Manufacturer Name": prod.get("mfr", ""),
                    "Brand Name": prod.get("mp_brLbl") or prod.get("mp_mLbl") or "",
                    "Item Name": prod.get("mp_des", ""),
                    "Full Product Description": " ".join(filter(None, [
                        prod.get("mp_bulletPoints"),
                        prod.get("mp_publicNotes"),
                        prod.get("mp_applicationUse")
                    ])),
                    "Price": next((p.get("pr") for p in prod.get("pdd", []) if p.get("dataName") == "Online Price:"), ""),
                    "Unit of Issue": prod.get("mp_uom", ""),
                    "Availability": prod.get("productEda", {}).get("mp_availabilityMessage", ""),
                    "pdp_url": f"https://www.fastenal.com/product/details/{prod.get('sku')}"
                }
                # Avoid duplicates
                self.products_collection.update_one(
                    {"sku": record["sku"]},
                    {"$set": record},
                    upsert=True
                )
            logging.info(f"{level_one} > {level_two} > {level_three} | Page {page}/{total_pages} | {len(products)} products")
            page += 1
            time.sleep(REQUEST_DELAY)

    def main(self):
        logging.info("Starting Fastenal Product Crawler...")
        categories = self.categories_collection.find()
        for lvl1 in categories:
            lvl1_name = lvl1.get("categoryLevelOne")
            for lvl2 in lvl1.get("subcategories", []):
                lvl2_name = lvl2.get("categoryLevelTwo")
                for lvl3 in lvl2.get("subcategories", []):
                    lvl3_name = lvl3.get("categoryLevelThree")
                    cat_id = lvl3.get("categoryId")

                    if lvl3_name and cat_id:
                        logging.info(f"🔹 Processing: {lvl1_name} > {lvl2_name} > {lvl3_name}")
                        self.fetch_products_for_category(lvl1_name, lvl2_name, lvl3_name, cat_id)
        logging.info("Crawl finished.")
        self.client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")
    crawler = Crawler()
    crawler.main()
