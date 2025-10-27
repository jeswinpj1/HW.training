import logging
import json
import re
import time
import requests
from mongoengine import connect, errors
from settings import HEADERS, MONGO_DB
from item import LidlProductItem
INPUT_FILE = "genrated_api_urls.txt"

class Crawler:
    """Lidl API Product Crawler"""

    def __init__(self):
        connect(db=MONGO_DB, alias="default", host="localhost", port=27017)

    def start(self):
        """Read category URLs & start crawling"""
        with open(INPUT_FILE, "r", encoding="utf-8") as file:
            for url in file:
                url = url.strip()
                if not url:
                    continue
                logging.info(f"Crawling URL: {url}")
                self.fetch_products(url)

    def fetch_products(self, base_url):
        """Pagination Logic (offset-based crawl)"""
        offset = 0
        page_size = 12

        while True:
            api_url = re.sub(r"offset=\d+", f"offset={offset}", base_url)
            response = requests.get(api_url, headers=HEADERS, timeout=10)
            data = response.json() # Convert API JSON text to Python dictionary(converts the API response)

            items = data.get("items", [])
            total = data.get("numFound") or data.get("keywordResults", {}).get("num_items_found", 0)

            if not items:
                logging.info("No more products. Pagination finished.")
                break

            for product in items:
                item = self.map_product(product) # converts raw API data into your required format.
                self.save_to_db(item)

            logging.info(f" Offset {offset} | Products Fetched: {len(items)}")

            offset += page_size
            if offset >= total:
                logging.info("Completed all pages for this category.")
                break

            time.sleep(0.2)
 
    def map_product(self, product):
            """Extract required fields from API response"""
            grid = product.get("gridbox", {}).get("data", {})
            price = grid.get("price", {})
            meta = product.get("gridbox", {}).get("meta", {})

            breadcrumbs = meta.get("wonCategoryBreadcrumbs", [])
            breadcrumb_names = []
            if isinstance(breadcrumbs, list) and len(breadcrumbs) > 0:
                    # First element is again a list of category dictionaries
                for bc in breadcrumbs[0]:
                    breadcrumb_names.append(bc.get("name", ""))

            breadcrumb_full = " > ".join(breadcrumb_names) if breadcrumb_names else ""
            # Split breadcrumb by '>' and clean each part
            hierarchy_parts = [b.strip() for b in breadcrumb_full.split(">") if b.strip()]

                # Create up to 7 hierarchy levels (fill missing ones with "")
            hierarchy_levels = {}
            for i in range(7):
                hierarchy_levels[f"producthierarchy_level{i+1}"] = hierarchy_parts[i] if i < len(hierarchy_parts) else ""

            supplemental = grid.get("keyfacts", {}).get("supplementalDescription", "")
            match = re.match(r"([\d.,]+)\s*(\w+)", supplemental)  # captures number + unit
            grammage_quantity = match.group(1) if match else ""
            grammage_unit = match.group(2) if match else ""
            
            # "In stock" → instock = True  "In store from 30.10" → instock = False
            stockAvailability = grid.get("stockAvailability", {}).get("badgeInfo", {}).get("badges", [{}])[0].get("text", "")
            if stockAvailability and not stockAvailability.lower().startswith("in store from"):
                instock = True
            else:
                instock = False
            print(price.get("oldPrice") or price.get("discount", {}).get("deletedPrice", ""))
            return {
                "unique_id": str(product.get("code", "")),
                "product_unique_key": str(product.get("code", "")) + "P",
                "brand": grid.get("brand", "").get("name", ""),
                "category": grid.get("category", ""),
                "product_type": grid.get("productType", ""),
                "grammage_quantity": grammage_quantity,
                "grammage_unit": grammage_unit,
                "competitor_name": "Lidl",
                "instock": instock,   
                "site_shown_uom": f"{grammage_quantity} {grammage_unit}".strip(),
                "price_per_unit": price.get("basePrice", {}).get("text", ""),
                "current_price": price.get("price", ""),
                "promotion_type": price.get("discount", {}).get("discountText", ""),
                "discount_price": price.get("discount", {}).get("price", ""),
                "product_name": grid.get("title", ""),
                "product_description": grid.get("keyfacts", {}).get("description", ""),
                    **hierarchy_levels,
                "breadcrumb": breadcrumb_full,
                "regular_price": price.get("price", "") or price.get("discount", {}).get("oldPrice", ""),
                "pdp_url": "https://www.lidl.co.uk" + grid.get("canonicalUrl", ""),
                "image_url_1": grid.get("imageList", [None])[0] if grid.get("imageList") else "",
                "store_name": "lidl",
                "extraction_date": "2025-10-27", 
                "currency": price.get("currencySymbol", ""),
            }
    
    def save_to_db(self, item):
        """Validate using LidlProductItem schema and insert into MongoDB"""
        try:
            product = LidlProductItem(**item)  # Validate using schema
            product.save()  # Save to MongoDB
            logging.info(f"Saved: {item.get('unique_id')}")
        except Exception as e:
            logging.warning(f"Skipping duplicate or invalid data: {e}")


if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        crawler = Crawler()
        crawler.start()
