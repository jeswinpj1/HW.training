import logging
import time
from urllib.parse import quote
from settings import (requests, session, headers, cookies,category_menu_url, product_search_url,MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_CATEGORY)
from pymongo import MongoClient
class Crawler:
    """Fastenal Recursive Category Crawler (No try/except, Simple Version)"""
    def __init__(self):
        """Initialize MongoDB"""
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db[MONGO_COLLECTION_CATEGORY]
    def start(self):
        """Fetch and save full category tree recursively"""
        logging.info(" Starting Fastenal Category Crawler...")
     # --- Recursive function inside start() ---
        def fetch_category_tree(base_info, visited=None):
            """Recursively fetch all subcategories for a given category"""
            if visited is None:
                visited = set()
            # --- Stop recursion if this category was already processed ---
            cat_id = base_info.get("categoryId")
            if cat_id in visited:
                logging.warning(f" Skipping already visited category {cat_id}")
                return base_info
            visited.add(cat_id)
            # --- Build the page URL ---
            category_levels = ["categoryLevelOne", "categoryLevelTwo", "categoryLevelThree", "categoryLevelFour"]
            url_parts = [base_info[level] for level in category_levels if base_info.get(level)]
            page_url = "/product/" + "/".join(quote(name) for name in url_parts)
            payload = dict(base_info)
            payload.update({
                "ignoreCounterBook": True,
                "attributeFilters": {},
                "pageUrl": page_url,
            })
            # --- Make API request ---
            for _ in range(3):
                resp = session.post(product_search_url, headers=headers, cookies=cookies, json=payload)
                if resp.status_code == 200:
                    break
                logging.warning(f" Retrying for: {cat_id} ...")
                time.sleep(1)
            else:
                logging.warning(f" Failed after retries: {base_info}")
                return base_info
            data = resp.json()
            subs = data.get("categoryList", [])
            # --- Stop recursion if no subcategories ---
            if not subs:
                return base_info
            # --- Process subcategories recursively ---
            base_info["subcategories"] = []
            for subcategory in subs:
                next_category_info = {}
                # Copy parent levels
                for key, value in base_info.items():
                    if "categoryLevel" in key or key == "categoryId":
                        next_category_info[key] = value
                # Add child details
                for key, value in subcategory.items():
                    if "categoryLevel" in key or key == "categoryId":
                        next_category_info[key] = value
                # Recursive call
                child_tree = fetch_category_tree(next_category_info, visited)
                base_info["subcategories"].append(child_tree)
                time.sleep(0.2)
            return base_info

        # --- Step 1: Fetch main categories ---
        response = session.get(category_menu_url, headers=headers, cookies=cookies)
        if response.status_code != 200:
            logging.error(" Failed to fetch main categories. Exiting.")
            return
        data = response.json()
        full_tree = []
        # --- Step 2: Crawl each top-level category ---
        for cat in data.get("categoryList", []):
            root = {"categoryLevelOne": cat.get("categoryLevelOne"),"categoryId": cat.get("categoryId")}
            logging.info(f" Crawling: {root['categoryLevelOne']} ({root['categoryId']})")
            tree = fetch_category_tree(root)
            full_tree.append(tree)
            # --- Save to MongoDB  ---
            inserted = False
            for _ in range(2):  # Sometimes, insertion can fail temporarily due to MongoDB network delay,Instead of crashing,the code just tries again once more after a short delay.
                result = self.collection.insert_one(tree)
                if result.inserted_id:
                    inserted = True
                    break
                logging.warning(f" Retrying DB insert for {root['categoryLevelOne']}...")
                time.sleep(1)
            if inserted:
                logging.info(f" Saved: {root['categoryLevelOne']}")
            else:
                logging.warning(f" Skipped DB save for {root['categoryLevelOne']}")
            time.sleep(0.3)
        # --- Step 4: Close MongoDB connection ---
        self.client.close()
        logging.info(" MongoDB connection closed.")
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")
    Crawler().start()
