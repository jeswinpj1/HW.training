# # category_crawler.py
# import logging
# from pymongo import MongoClient
# from settings import MONGO_DB

# class CategoryCrawler:
#     """Stores category IDs into DB"""

#     def __init__(self):
#         self.mongo = MongoClient("mongodb://localhost:27017/")[MONGO_DB]
#         self.cat_col = self.mongo["lidl_categories"]

#     def seed_categories(self):
#         logging.info("Seeding categories into DB...")

#         categories = [
#             {"category_id":"10068374"},
#             {"category_id":"10068166"},
#             {"category_id":"10068222"},
#             {"category_id":"10068226"},
#             {"category_id":"10068371"},
#             {"category_id":"10068373"},
#             {"category_id":"10068225"}
#         ]

#         self.cat_col.delete_many({})
#         self.cat_col.insert_many(categories)

#         logging.info("✔ Categories stored successfully\n")


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     CategoryCrawler().seed_categories()



# category_crawler.py

import logging
import re
import requests
from scrapy import Selector
from pymongo import MongoClient
from settings import MONGO_DB, HEADERS


class CategoryCrawler:
    """Extract category IDs from Lidl website and store in MongoDB"""

    def __init__(self):
        self.mongo = MongoClient("mongodb://localhost:27017/")[MONGO_DB]
        self.cat_col = self.mongo["lidl_categories"]

    def fetch_and_store_categories(self):
        logging.info("Fetching category IDs from Lidl website...")

        url = "https://www.lidl.co.uk"   # <-- PUT THE REAL CATEGORY PAGE HERE

        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        selector = Selector(text=response.text)


        # Extract all slider category links
        links = selector.xpath('//a[contains(@class, "ACategoryOverviewSlider__Link")]/@href').getall()

        if not links:
            logging.warning("No category links found!")
            return

        # Clear old categories
        self.cat_col.delete_many({})
        saved = 0

        for link in links:
            # Extract numeric category ID using your regex logic
            match = re.search(r's(\d+)', link)

            if match:
                category_id = match.group(1)

                # Store into MongoDB (id only)
                self.cat_col.insert_one({"category_id": category_id})
                saved += 1
                logging.info(f"Saved category ID: {category_id}")

        logging.info(f"✔ Total categories saved: {saved}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    CategoryCrawler().fetch_and_store_categories()
