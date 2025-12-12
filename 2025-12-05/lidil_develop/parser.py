import logging
import requests
from parsel import Selector
from settings import HEADERS, MONGO_DB, MONGO_COLLECTION_DATA_FULL, MONGO_COLLECTION_DATA
from pymongo import MongoClient


class Parser:
    """Parser for extracting material and discount from Lidl PDP pages."""

    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.mongo = self.client[MONGO_DB]
        self.queue = None

    def start(self):
        logging.info("Starting PDP parser...")

        collection = self.mongo[MONGO_COLLECTION_DATA]
        count = collection.count_documents({})
        logging.info(f"Products in Mongo: {count}")

        if count == 0:
            logging.warning("No products found. Run crawler first.")
            return

        processed_count = 0

        for product in collection.find():
            # Detect URL field
            purl = product.get("url") or product.get("pdp_url")
            if not purl:
                logging.warning(f"No URL found for product: {product.get('unique_id')}")
                continue

            logging.info(f"Processing: {purl}")

            # Inline fetch with retry
            resp = None
            for attempt in range(3):
                try:
                    temp = requests.get(purl, headers=HEADERS, timeout=10)
                    if temp.status_code == 200:
                        resp = temp
                        break
                    else:
                        logging.warning(f"Status {temp.status_code} for {purl}")
                except Exception as e:
                    logging.warning(f"Retry {attempt+1}/3 failed for {purl}: {e}")

            if not resp:
                logging.error(f"FAILED: Could not fetch URL after retries: {purl}")
                continue

            # Parse and save
            try:
                saved = self.parse_item(purl, resp, product)
                if saved:
                    processed_count += 1
            except Exception:
                logging.exception(f"ERROR while parsing: {purl}")

        logging.info(f"Parsing complete. Total products processed: {processed_count}")

    def parse_item(self, url, response, product=None):
        """Extract material info + discount and save with duplicate check."""
        sel = Selector(response.text)

        MATERIAL_XPATH = "//div[@class='info-content']//li/text()"
        DISCOUNT_XPATH = "//span[contains(@class,'ods-price__box-content-text-el')]/text()"

        materials = sel.xpath(MATERIAL_XPATH).getall()
        discount = sel.xpath(DISCOUNT_XPATH).getall()

        material = ", ".join(m.strip() for m in materials if m.strip())
        dress_discount = discount[0].strip() if discount else ""

        item = {}
        item["url"] = url
        item["material"] = material
        item["promotion_description"] = dress_discount
        item["product_id"] = product.get("product_id")
        item["unique_id"] = product.get("unique_id")
        item["product_unique_key"] = product.get("product_unique_key")
        item["brand"] = product.get("brand")
        item["category"] = product.get("category", "")
        item["product_type"] = product.get("product_type", "")
        item["grammage_quantity"] = product.get("grammage_quantity", "")
        item["grammage_unit"] = product.get("grammage_unit", "")
        item["competitor_name"] = "Lidl"
        item["instock"] = product.get("instock", "")
        item["site_shown_uom"] = product.get("site_shown_uom", "")
        item["price_per_unit"] = product.get("price_per_unit", "")
        item["product_name"] = product.get("product_name", "")
        item["product_description"] = product.get("product_description", "")
        item["breadcrumb"] = product.get("breadcrumb", "")
        item["producthierarchy_level1"] = product.get("producthierarchy_level1", "")
        item["producthierarchy_level2"] = product.get("producthierarchy_level2", "")
        item["producthierarchy_level3"] = product.get("producthierarchy_level3", "")
        item["producthierarchy_level4"] = product.get("producthierarchy_level4", "")
        item["producthierarchy_level5"] = product.get("producthierarchy_level5", "")
        item["producthierarchy_level6"] = product.get("producthierarchy_level6", "")
        item["producthierarchy_level7"] = product.get("producthierarchy_level7", "")
        item["regular_price"] = product.get("regular_price", "")
        item["price_was"] = product.get("price_was", "")
        item["promotion_price"] = product.get("promotion_price", "")
        item["selling_price"] = product.get("selling_price", "")
        item["promotion_type"] = product.get("promotion_type", "")
        item["percentage_discount"] = product.get("percentage_discount", "")
        item["currency"] = "GBP"
        item["pdp_url"] = product.get("pdp_url", "")
        item["image_url_1"] = product.get("image_url_1", "")
        item["extraction_date"] = "2025-12-12"
        
        # Duplicate check
        key = {"unique_id": item["unique_id"]}
        if not self.mongo[MONGO_COLLECTION_DATA_FULL].find_one(key):
            try:
                self.mongo[MONGO_COLLECTION_DATA_FULL].insert_one({**key, **item})
                logging.info(f"SAVED: {url}")
                return True
            except Exception:
                logging.exception(f"Mongo Insert Error: {url}")
                return False
        else:
            logging.info(f"Already exists: {url}")
            return False

    def close(self):
        if self.client:
            self.client.close()
        if self.queue:
            try:
                self.queue.close()
            except:
                pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()
