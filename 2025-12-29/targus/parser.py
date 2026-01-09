import logging
import requests
from pymongo import MongoClient
from settings import HEADERS, MONGO_DB, MONGO_COLLECTION_DATA


class Parser:
    """FastSimon Auto Category Parser"""

    def __init__(self):
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.mongo = self.mongo_client[MONGO_DB]

        self.base_api = "https://api.fastsimon.com/categories_navigation"
        self.store_id = "7553024066"
        self.uuid = "8fb07dc3-f0b7-4ea1-bc29-4286c08e8c3f"
        self.products_per_page = 63

        # Seed category (ANY valid category works)
        self.seed_category_id = "162323857474"

        # Will be auto-filled
        self.category_ids = set()
        self.processed_categories = set()

    # --------------------------------------------------
    # START
    # --------------------------------------------------
    def start(self):
        logging.info("Starting category discovery")

        # 1️⃣ Discover categories from seed
        self.discover_categories(self.seed_category_id)

        logging.info(f"Total categories discovered: {len(self.category_ids)}")

        # 2️⃣ Paginate each discovered category
        for category_id in self.category_ids:
            if category_id in self.processed_categories:
                continue

            logging.info(f"Processing category: {category_id}")
            self.paginate_category(category_id)
            self.processed_categories.add(category_id)

    # --------------------------------------------------
    # DISCOVER CATEGORY IDS
    # --------------------------------------------------
    def discover_categories(self, category_id):
        page = 1

        while True:
            params = {
                "request_source": "v-next",
                "src": "v-next",
                "UUID": self.uuid,
                "uuid": self.uuid,
                "store_id": self.store_id,
                "api_type": "json",
                "category_id": category_id,
                "facets_required": 1,
                "products_per_page": self.products_per_page,
                "page_num": page,
                "with_product_attributes": "true",
                "qs": "false",
            }

            response = requests.get(
                self.base_api,
                headers=HEADERS,
                params=params,
                timeout=30
            )

            if not response or response.status_code != 200:
                break

            items = response.json().get("items", [])

            if not items:
                break

            for product in items:
                for att in product.get("att", []):
                    if att[0] == "Categories":
                        for cat in att[1]:
                            if cat and isinstance(cat, list):
                                self.category_ids.add(cat[0])

            page += 1

    # --------------------------------------------------
    # CATEGORY PAGINATION
    # --------------------------------------------------
    def paginate_category(self, category_id):
        page = 1

        while True:
            params = {
                "request_source": "v-next",
                "src": "v-next",
                "UUID": self.uuid,
                "uuid": self.uuid,
                "store_id": self.store_id,
                "api_type": "json",
                "category_id": category_id,
                "facets_required": 1,
                "products_per_page": self.products_per_page,
                "page_num": page,
                "with_product_attributes": "true",
                "qs": "false",
            }

            response = requests.get(
                self.base_api,
                headers=HEADERS,
                params=params,
                timeout=30
            )

            if not response or response.status_code != 200:
                break

            items = response.json().get("items", [])

            logging.info(
                f"Category {category_id} | Page {page} | Products {len(items)}"
            )

            if not items:
                break

            for product in items:
                self.parse_item(category_id, product)

            page += 1

    # --------------------------------------------------
    # PARSE ITEM
    # --------------------------------------------------
    def parse_item(self, category_id, product):
        item = {}

        item["website"] = "Targus"
        item["category_id"] = category_id

        item["product_id"] = product.get("id")
        item["name"] = product.get("l")
        item["product_url"] = product.get("u")

        item["sku"] = product.get("sku")
        item["skus"] = product.get("skus")

        item["currency"] = product.get("c")
        item["price"] = product.get("p")
        item["compare_price"] = product.get("p_c")

        item["image"] = product.get("t")
        item["thumbnail"] = product.get("t2")

        item["instock"] = product.get("v_c") == 1
        item["sellable"] = product.get("f") == 0

        # Attributes
        attributes = {}
        for att in product.get("att", []):
            if len(att) == 2:
                attributes[att[0]] = att[1]

        item["attributes"] = attributes
        item["variant_attributes"] = product.get("vra", [])

        logging.info(item)

        try:
            self.mongo[MONGO_COLLECTION_DATA].insert_one(item)
        except Exception as e:
            logging.error(e)

    # --------------------------------------------------
    # CLOSE
    # --------------------------------------------------
    def close(self):
        self.mongo_client.close()


# --------------------------------------------------
# MAIN
# --------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = Parser()
    parser.start()
    parser.close()
