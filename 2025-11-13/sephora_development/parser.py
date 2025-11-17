import logging
import time
import requests
import re
from urllib.parse import urlparse
from settings import (HEADERS, BASE_API, INCLUDE_PARAMS, collection_categories, collection_products, client)
from items import ProductItem  

class Parser:
    """Sephora API Product Parser — Clean Working Version"""
    def __init__(self):
        self.mongo = client

    def start(self):
        docs = list(collection_categories.find({}, {"products": 1}))
        total = sum(len(doc.get("products", [])) for doc in docs)
        logging.info(f"Total Product URLs: {total}")
        count = 0
        for doc in docs:
            for url in doc.get("products", []):
                count += 1
                logging.info(f"[{count}/{total}] → {url}")
                parts = urlparse(url).path.strip("/").split("/")
                if len(parts) < 2:
                    logging.error(f"Invalid URL → {url}")
                    continue

                product_slug = parts[1]
                variant = parts[3] if len(parts) > 3 else None
                # Default API
                api = f"{BASE_API}{product_slug}?include={INCLUDE_PARAMS}"
                if variant:
                    api = f"{BASE_API}{product_slug}?v={variant}&include={INCLUDE_PARAMS}"
                logging.info(f"API → {api}")
                res = requests.get(api, headers=HEADERS)
                
                # Retry without variant if 422
                if res.status_code == 422:
                    res = requests.get(f"{BASE_API}{product_slug}?include={INCLUDE_PARAMS}", headers=HEADERS)
                
                if res.status_code != 200:
                    logging.error(f"API Failed {res.status_code} → {url}")
                    continue
                    
                response_json = res.json()
                self.parse_item(url, response_json)
                time.sleep(1)

    def parse_item(self, url, data):

        data_obj = data.get("data", {})
        attr = data_obj.get("attributes", {})
        included = data.get("included") or []
        ALLOWED_SKIN_TYPES = {"Combination", "Dry", "Normal", "Oily"}
        skin_types = []

        for obj in included:
            attrs = obj.get("attributes", {})
            value = attrs.get("value")
            filter_type = attrs.get("filter-type-id")

            if filter_type == 41 and value in ALLOWED_SKIN_TYPES:
                skin_types.append(value)

        clean_skin_type = list(set(skin_types))
        path = urlparse(url).path
        qty, unit = (None, None)

        if "/v/" in path:
            size_part = path.split("/v/")[-1]  # example → "30ml"
            match = re.search(r"(\d+\.?\d*)\s*(ml|g|oz|kg|mg|l)", size_part.lower())
            if match:
                qty, unit = match.group(1), match.group(2)

        # If qty not found in URL -> try from product name
        if not qty:
            name_text = attr.get("name", "").lower()
            match = re.search(r"(\d+\.?\d*)\s*(ml|g|oz|kg|mg|l)", name_text)
            if match:
                qty, unit = match.group(1), match.group(2)

        clean_ingredients   = attr.get("ingredients")
        clean_directions    = attr.get("how_to")
        clean_disclaimer    = attr.get("safety_warning")
        clean_description   = attr.get("description")

        # Mapping to ProductItem (generic + specific fields)
        item = {
            "url": url,
            "product_name": attr.get("name"),
            "brand": attr.get("brand-name"),
            "currency": "SGD",
            
            # Sephora Specifics
            "retailer_id": data_obj.get("id"),
            "retailer": "Sephora SG",
            "grammage_quantity": qty,
            "grammage_unit": unit,
            "original_price": attr.get("display-original-price"),
            "selling_price": attr.get("display-price"),
            "promotion_description": attr.get("sale-text"),
            "pdp_url": url,
            "image_url": attr.get("image-urls") or [],
            "ingredients": clean_ingredients,
            "directions": clean_directions,
            "disclaimer": clean_disclaimer,
            "description": clean_description,
            "diet_suitability": attr.get("diet_suitability"),
            "colour": attr.get("colour"),
            "hair_type": attr.get("hair_type"),
            "skin_type": clean_skin_type,
            "skin_tone": None,
        }
        
        try:
            # Using ProductItem from items.py
            final_item = ProductItem(**item)
            # Convert MongoEngine doc to dict for PyMongo insertion
            collection_products.insert_one(final_item.to_mongo().to_dict())
            logging.info(f"Saved → {item['product_name']}")
        except Exception as e:
            logging.error(f"Save Error → {e}")

    def close(self):
        self.mongo.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    Parser().start()
    Parser().close()


