import logging
import json
import time
import re
import requests
from settings import HEADERS as headers, MONGO_DB
from pymongo import MongoClient
from datetime import datetime
from lxml import html


class Crawler:
    """Lidl API Product Crawler"""

    def __init__(self):
        self.mongo = MongoClient("mongodb://localhost:27017/")[MONGO_DB]
        self.cat_col = self.mongo["lidl_categories"]
        self.prod_col = self.mongo["lidl_products"]

    def start(self):
        """Requesting Start url"""
        logging.info("Starting Lidl Crawl")

        # READ CATEGORY IDs FROM DB
        for row in self.cat_col.find():
            cat_id = row["category_id"]
            logging.info(f"\nCrawling Category: {cat_id}")

            meta = {}
            meta['category_id'] = cat_id
            offset = meta.get("offset", 0)  # initialising offset for pagination
            
            # generate api Url
            api_url = (
                "https://www.lidl.co.uk/q/api/search?"
                f"category.id={cat_id}&offset={offset}&fetchsize=12&locale=en_GB&assortment=GB&version=2.1.0"
            )

            while True:
                logging.info(f"Fetching: {api_url}")
                time.sleep(1)
                
                response = requests.get(api_url, headers=headers)
                if response.status_code == 200:
                    is_next = self.parse_item(response, meta)
                    if not is_next:
                        logging.info("Pagination completed")
                        break
                    
                    # pagination crawling
                    offset += 12
                    cat_id = meta['category_id']
                    api_url = (
                        "https://www.lidl.co.uk/q/api/search?"
                        f"category.id={cat_id}&offset={offset}&fetchsize=12&locale=en_GB&assortment=GB&version=2.1.0"
                    )
                    meta["offset"] = offset
                else:
                    logging.error(f"Status {response.status_code}")
                    logging.info("No data or error... stopping pagination")
                    break

    def parse_item(self, response, meta):
        """item part"""
        data = response.json()
        items = data.get("items", [])
        total = data.get("numFound", 0)
        offset = meta.get("offset", 0)

        if items:
            for p in items:
                grid = p.get("gridbox", {}).get("data", {})
                price = grid.get("price", {})
                lidl_plus = grid.get("lidlPlus", [])
                product_meta = p.get("gridbox", {}).get("meta", {})
                stock = grid.get("stockAvailability", {})
                badges = stock.get("badgeInfo", {}).get("badges", [])
                
                pdp_url = f"https://www.lidl.co.uk{grid.get('canonicalUrl', '')}"

                # Extract material and discount from HTML
                material = ""
                dress_discount = ""
                try:
                    res = requests.get(pdp_url, headers=headers, timeout=10)
                    if res.status_code == 200:
                        tree = html.fromstring(res.text)

                        materials = tree.xpath("//div[@class='info-content']//li/text()")
                        if materials:
                            material = ", ".join([m.strip() for m in materials if m.strip()])

                        discount = tree.xpath("//span[contains(@class,'ods-price__box-content-text-el')]/text()")
                        if discount:
                            dress_discount = discount[0].strip()
                except Exception:
                    pass

                # Extract prices
                price = price if isinstance(price, dict) else {}
                lidl_plus = lidl_plus if isinstance(lidl_plus, list) else []

                # --------------- CASE 1: Lidl Plus ---------------
                if lidl_plus:
                    lp = lidl_plus[0]
                    lp_price = lp.get("price", {}) or {}
                    lp_disc = lp_price.get("discount", {}) or {}

                    regular_price = (
                        lp_disc.get("deletedPrice")
                        or lp_price.get("deletedPrice")
                        or lp_price.get("oldPrice")
                        or price.get("oldPrice")
                    )

                    selling_price = (
                        lp_price.get("price")
                        or price.get("price")
                    )
                    discount_text = (
                        lp_disc.get("discountText")
                        or price.get("discountText")
                        or ""
                    )

                    # Extract only number → "SAVE 34%" → "34"
                    percentage_discount = (
                        re.search(r"\d+", discount_text).group(0)
                        if re.search(r"\d+", discount_text)
                        else ""
                    )
                    price_fields = {
                        "regular_price": regular_price or "",
                        "price_was": regular_price or "",
                        "promotion_price": selling_price or "",
                        "selling_price": selling_price or "",
                        "promotion_type": "Lidl Plus",
                        "discount_text": discount_text,
                        "percentage_discount": percentage_discount
                    }

                # --------------- CASE 2: Standard Discount ---------------
                elif isinstance(price.get("discount", {}), dict) and price.get("discount", {}).get("deletedPrice"):
                    discount = price.get("discount", {})
                    regular_price = (
                        discount.get("deletedPrice")
                        or discount.get("oldPrice")
                    )

                    selling_price = discount.get("price") or price.get("price")

                    price_fields = {
                        "regular_price": regular_price or "",
                        "price_was": regular_price or "",
                        "promotion_price": selling_price or "",
                        "selling_price": selling_price or "",
                        "promotion_type": discount.get("discountText", ""),
                        "discount_text": discount.get("discountText", ""),
                        "percentage_discount": discount.get("percentageDiscount", "")
                    }

                # --------------- CASE 3: No Discount ---------------
                else:
                    normal_price = price.get("price") or price.get("oldPrice")

                    price_fields = {
                        "regular_price": normal_price or "",
                        "price_was": "",
                        "promotion_price": "",
                        "selling_price": normal_price or "",
                        "promotion_type": "",
                        "discount_text": "",
                        "percentage_discount": ""
                    }

                currency_symbol = price.get("displayedCurrency", "")

                # --- Breadcrumbs ---
                breadcrumbs = product_meta.get("wonCategoryBreadcrumbs", [])
                names = [bc.get("name", "") for bc in (breadcrumbs[0] if breadcrumbs else [])]
                breadcrumb_full = " > ".join(names)
                levels = {f"producthierarchy_level{i+1}": names[i] if i < len(names) else "" for i in range(7)}

                # --- Grammatical info ---
                raw_grammage = grid.get("keyfacts", {}).get("supplementalDescription", "")

                grammage_quantity = ""
                grammage_unit = ""

                if raw_grammage:
                    # 1) Replace comma decimal → 2,2 → 2.2
                    cleaned = raw_grammage.replace(",", ".")

                    # 2) Handle ranges like "2.4 - 2.8kg" or "2.4–2.8 kg"
                    range_match = re.search(r"([\d.]+)\s*[-–]\s*([\d.]+)\s*(kg|g|ml|l|cl)?", cleaned, re.I)
                    if range_match:
                        q1 = range_match.group(1)
                        q2 = range_match.group(2)
                        unit = range_match.group(3) or ""

                        grammage_quantity = f"{q1} - {q2}"
                        grammage_unit = unit
                    else:
                        # 3) Single value like "2.2kg", "500 g", "1 l"
                        single_match = re.search(r"([\d.]+)\s*(kg|g|ml|l|cl)", cleaned, re.I)
                        if single_match:
                            grammage_quantity = single_match.group(1)
                            grammage_unit = single_match.group(2)

                # --- Stock handling ---
                instock = True
                if badges:
                    text, typ = badges[0].get("text", "").lower(), badges[0].get("type", "").upper()
                    if text.startswith("in store from") or "FROM_FUTURE" in typ:
                        instock = False
                    elif "available in store now" in text or "PAST_DATE_RANGE" in typ or "IN_STORE_PAST" in typ:
                        instock = True
                    else:
                        instock = ""
                elif stock.get("availabilityIndicator") is not None:
                    instock = bool(int(stock["availabilityIndicator"]))

                # ITEM YIELD
                item = {}
                item["unique_id"] = str(p.get("code", ""))
                item["product_unique_key"] = f"{p.get('code', '')}P"
                item["brand"] = grid.get("brand", {}).get("name", "")
                item["category"] = grid.get("category", "")
                item["product_type"] = grid.get("productType", "")
                item["grammage_quantity"] = grammage_quantity
                item["grammage_unit"] = grammage_unit
                item["competitor_name"] = "Lidl"
                item["material"] = material
                item["discount_text_full"] = dress_discount
                item["instock"] = instock
                item["site_shown_uom"] = f"{grammage_quantity} {grammage_unit}".strip()
                item["price_per_unit"] = price.get("basePrice", {}).get("text", "")
                item["product_name"] = grid.get("title", "")
                item["product_description"] = grid.get("keyfacts", {}).get("description", "") or grid.get("keyfacts", {}).get("supplementalDescription", "")
                item["breadcrumb"] = breadcrumb_full
                item["producthierarchy_level1"] = levels.get("producthierarchy_level1", "")
                item["producthierarchy_level2"] = levels.get("producthierarchy_level2", "")
                item["producthierarchy_level3"] = levels.get("producthierarchy_level3", "")
                item["producthierarchy_level4"] = levels.get("producthierarchy_level4", "")
                item["producthierarchy_level5"] = levels.get("producthierarchy_level5", "")
                item["producthierarchy_level6"] = levels.get("producthierarchy_level6", "")
                item["producthierarchy_level7"] = levels.get("producthierarchy_level7", "")
                item["regular_price"] = price_fields["regular_price"]
                item["price_was"] = price_fields["price_was"]
                item["promotion_price"] = price_fields["promotion_price"]
                item["selling_price"] = price_fields["selling_price"]
                item["promotion_type"] = price_fields["promotion_type"]
                item["percentage_discount"] = price_fields["percentage_discount"]
                item["currency"] = "GBP"
                item["pdp_url"] = pdp_url
                item["image_url_1"] = grid.get("imageList", [""])[0]
                item["extraction_date"] = "2025-12-12"

                logging.info(item)
                try:
                    key = {"unique_id": item["unique_id"]}
                    self.prod_col.update_one(key, {"$set": item}, upsert=True)
                    logging.info(f"Saved: {item['product_name']}")
                except:
                    pass

            # Check if there are more items to fetch
            if offset + 12 < total:
                return True
        return False

    def close(self):
        """Close function for all module object closing"""
        self.mongo.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    crawler = Crawler()
    crawler.start()
    crawler.close()