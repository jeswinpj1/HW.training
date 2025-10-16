# # parser.py
# import re
# import time
# import logging
# import requests
# from lxml import html
# from pymongo import MongoClient
# from datetime import datetime
# from settings import HEADERS_PAGE, MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_DATA, MONGO_COLLECTION_ENRICHED_DATA, REQUEST_DELAY, GRAMMAGE_REGEX

# logging.basicConfig(level=logging.INFO)
# mongo_client = MongoClient(MONGO_URI)
# col_source = mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_DATA]
# col_enriched = mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_ENRICHED_DATA]

# # Define full 126 field list (normalized field names). Add any missing exact names to match your validator.
# FIELDS_126 = [
#     "unique_id","competitor_name","store_name","store_addressline1","store_addressline2","store_suburb",
#     "store_state","store_postcode","store_addressid","extraction_date","product_name","brand","brand_type",
#     "grammage_quantity","grammage_unit","drained_weight","producthierarchy_level1","producthierarchy_level2",
#     "producthierarchy_level3","producthierarchy_level4","producthierarchy_level5","producthierarchy_level6",
#     "producthierarchy_level7","regular_price","selling_price","price_was","promotion_price","promotion_valid_from",
#     "promotion_valid_upto","promotion_type","percentage_discount","promotion_description","package_sizeof_sellingprice",
#     "per_unit_sizedescription","price_valid_from","price_per_unit","multi_buy_item_count","multi_buy_items_price_total",
#     "currency","breadcrumb","pdp_url","variants","product_description","instructions","storage_instructions",
#     "preparationinstructions","instructionforuse","country_of_origin","allergens","age_of_the_product","age_recommendations",
#     "flavour","nutritions","nutritional_information","vitamins","labelling","grade","region","packaging","receipies",
#     "processed_food","barcode","frozen","chilled","organictype","cooking_part","Handmade","max_heating_temperature",
#     "special_information","label_information","dimensions","special_nutrition_purpose","feeding_recommendation","warranty",
#     "color","model_number","material","usp","dosage_recommendation","tasting_note","food_preservation","size","rating",
#     "review","file_name_1","image_url_1","file_name_2","image_url_2","file_name_3","image_url_3","competitor_product_key",
#     "fit_guide","occasion","material_composition","style","care_instructions","heel_type","heel_height","upc","features",
#     "dietary_lifestyle","manufacturer_address","importer_address","distributor_address","vinification_details","recycling_information",
#     "return_address","alchol_by_volume","beer_deg","netcontent","netweight","site_shown_uom","ingredients","random_weight_flag",
#     "instock","promo_limit","product_unique_key","multibuy_items_pricesingle","perfect_match","servings_per_pack","Warning",
#     "suitable_for","standard_drinks","environmental","grape_variety","retail_limit"
# ]

# RE_GRAM = re.compile(GRAMMAGE_REGEX, re.IGNORECASE)
# RE_PRICE = re.compile(r"([0-9]+[.,]?[0-9]*)")

# def safe_text(tree, xpath_expr):
#     """Return normalized string for xpath; handles lists"""
#     try:
#         # try normalize-space in xpath when possible
#         res = tree.xpath(f'normalize-space({xpath_expr})')
#         if res:
#             return res.strip()
#     except Exception:
#         pass
#     try:
#         values = tree.xpath(xpath_expr)
#         if isinstance(values, list):
#             text = " ".join([v.strip() for v in values if isinstance(v, str) and v.strip()])
#             return text.strip()
#         return str(values).strip()
#     except Exception:
#         return ""

# class Parser:
#     def __init__(self):
#         self.src = col_source
#         self.dst = col_enriched

#     def fetch_page(self, url):
#         if not url:
#             return None
#         try:
#             r = requests.get(url, headers=HEADERS_PAGE, timeout=30)
#             if r.status_code != 200:
#                 logging.error("Failed fetch %s -> %s", url, r.status_code)
#                 return None
#             return html.fromstring(r.text)
#         except Exception as e:
#             logging.error("Fetch error %s -> %s", url, e)
#             return None

#     def parse_grammage(self, text):
#         if not text:
#             return "", ""
#         m = RE_GRAM.search(text)
#         if not m:
#             return "", ""
#         qty = m.group(1).replace(",", ".")
#         unit = m.group(2).lower()
#         if unit == "lt":
#             unit = "l"
#         return qty, unit

#     def parse_price(self, text):
#         if not text:
#             return ""
#         m = RE_PRICE.search(text)
#         if not m:
#             return ""
#         try:
#             return f"{float(m.group(1).replace(',', '.')):.2f}"
#         except Exception:
#             return m.group(1)

#     def extract_from_tree(self, tree):
#         d = {}
#         if tree is None:
#             return d

#         # product name + brand
#         d["product_name"] = safe_text(tree, "//h1[@data-test='product-title']/text()")
#         d["brand"] = safe_text(tree, "//a[@data-test='product-information-brand']/text()")

#         # price
#         price_text = safe_text(tree, "//div[@data-test='product-price-type']//div[contains(@class,'__value')]/text()")
#         d["regular_price"] = self.parse_price(price_text)
#         d["price_per_unit"] = safe_text(tree, "//div[@data-test='product-price-type']//div[contains(@class,'__label')]/text()")
#         d["currency"] = "EUR" if d.get("regular_price") else ""

#         # sku / unique id
#         sku = safe_text(tree, "//div[@data-test='product-sku']/text()")
#         if sku:
#             d["unique_id"] = sku.replace("Item No.:", "").strip()
#         else:
#             d["unique_id"] = ""

#         # images
#         d["image_url_1"] = safe_text(tree, "//img[@data-test='product-detail-image']/@src")
#         d["file_name_1"] = f"{d.get('unique_id','')}_1.PNG" if d.get("unique_id") else ""

#         # description, breadcrumb
#         d["product_description"] = safe_text(tree, "string(//div[contains(@class,'ws-product-slug-main__description-short')])")
#         breadcrumbs = tree.xpath("//ul[contains(@class,'ws-product-information__piece-description')]//li//text()")
#         d["breadcrumb"] = " > ".join([b.strip() for b in breadcrumbs if b.strip()]) if breadcrumbs else ""

#         # nutrition table
#         try:
#             names = tree.xpath("//table[contains(@class,'ws-product-detail-nutrition-table')]//th[@scope='row']/text()")
#             vals = tree.xpath("//table[contains(@class,'ws-product-detail-nutrition-table')]//td/text()")
#             nutrit = []
#             for n, v in zip(names, vals):
#                 nutrit.append(f"{n.strip()}: {v.strip()}")
#             d["nutritions"] = " | ".join(nutrit)
#         except Exception:
#             d["nutritions"] = ""

#         # product detail rows by titles (german terms from snippet) - fallback to english-like titles
#         def row(title_variants):
#             for t in title_variants:
#                 xp = f"//div[contains(@class,'ws-product-detail-row')][.//div[contains(@class,'ws-product-detail-row__title')][contains(normalize-space(.),'{t}')]]//div[contains(@class,'ws-product-detail-row__content')]//text()"
#                 val = tree.xpath(xp)
#                 if val:
#                     return " ".join([x.strip() for x in val if x.strip()])
#             return ""

#         d["ingredients"] = row(["Zutaten", "Ingredients"])
#         d["allergens"] = row(["Allergene", "Allergens"])
#         d["storage_instructions"] = row(["storage", "Aufbewahrung", "Lagerung"])
#         d["manufacturer_address"] = row(["Manufacturer", "Hersteller", "Kontakt", "contact"])
#         d["country_of_origin"] = row(["Country of production", "Ursprungsland"])
#         d["packaging"] = row(["Verpackung", "packaging", "Packaging"])
#         d["netcontent"] = row(["Net content", "Nettofüllmenge", "Net content"])

#         # instock
#         add_to_cart_btn = tree.xpath("//button[contains(@class,'ws-product-actions__add-to-cart')]")
#         d["instock"] = "TRUE" if add_to_cart_btn else "FALSE"

#         # grammage from title/subtitle/description
#         text_source = " ".join([d.get("product_name",""), safe_text(tree, "//ul[@data-test='product-information-piece-description']//li[1]/text()"), d.get("product_description","")])
#         qty, unit = self.parse_grammage(text_source)
#         d["grammage_quantity"] = qty
#         d["grammage_unit"] = unit

#         return d

#     def parse_item(self, product):
#         pdp_url = product.get("pdp_url") or product.get("url") or ""
#         tree = self.fetch_page(pdp_url) if pdp_url else None
#         tree_data = self.extract_from_tree(tree)

#         # Merge: product (source) takes precedence, then scraped
#         enriched = {}
#         for f in FIELDS_126:
#             enriched[f] = product.get(f, "") or tree_data.get(f, "") or ""

#         # ensure minimal mandatory fields
#         enriched["unique_id"] = enriched.get("unique_id") or product.get("unique_id") or product.get("sku") or ""
#         enriched["competitor_name"] = enriched.get("competitor_name") or product.get("competitor_name") or "Billa"
#         enriched["extraction_date"] = enriched.get("extraction_date") or datetime.now().strftime("%Y-%m-%d")
#         enriched["pdp_url"] = enriched.get("pdp_url") or pdp_url

#         # image file naming ensure PNG
#         if enriched.get("image_url_1") and not enriched.get("file_name_1"):
#             uid = enriched.get("unique_id","")
#             enriched["file_name_1"] = f"{uid}_1.PNG" if uid else ""

#         try:
#             self.dst.update_one({"unique_id": enriched["unique_id"]}, {"$set": enriched}, upsert=True)
#             logging.info("Enriched & saved: %s (%s)", enriched.get("product_name"), enriched.get("unique_id"))
#         except Exception as e:
#             logging.error("Save error %s: %s", enriched.get("unique_id"), e)

#     def start(self):
#         items = list(self.src.find({}))
#         logging.info("Loaded %s items for enrichment", len(items))
#         for prod in items:
#             try:
#                 self.parse_item(prod)
#             except Exception as e:
#                 logging.error("Parse error for product: %s", e)
#             time.sleep(REQUEST_DELAY)


# if __name__ == "__main__":
#     Parser().start()


#>>>>>>>>>>>>>>>>>>>>>>>>>>............................>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..............>>>>>>>>>>>>>>>>>>>............>>>>>>>>>>>..

# parser.py
import re
import time
import logging
import requests
from pymongo import MongoClient
from datetime import datetime
from settings import (
    HEADERS_PAGE, 
    MONGO_URI, 
    MONGO_DB_NAME, 
    MONGO_COLLECTION_DATA, 
    MONGO_COLLECTION_ENRICHED_DATA, 
    REQUEST_DELAY, 
    GRAMMAGE_REGEX,
    CLIENT_NAME,
    STORE_ID,
    EXTRACTION_DATE
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

mongo_client = MongoClient(MONGO_URI)
col_source = mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_DATA]
col_enriched = mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_ENRICHED_DATA]

# 126 fields
FIELDS_126 = [
    "unique_id","competitor_name","store_name","store_addressline1","store_addressline2","store_suburb",
    "store_state","store_postcode","store_addressid","extraction_date","product_name","brand","brand_type",
    "grammage_quantity","grammage_unit","drained_weight","producthierarchy_level1","producthierarchy_level2",
    "producthierarchy_level3","producthierarchy_level4","producthierarchy_level5","producthierarchy_level6",
    "producthierarchy_level7","regular_price","selling_price","price_was","promotion_price","promotion_valid_from",
    "promotion_valid_upto","promotion_type","percentage_discount","promotion_description","package_sizeof_sellingprice",
    "per_unit_sizedescription","price_valid_from","price_per_unit","multi_buy_item_count","multi_buy_items_price_total",
    "currency","breadcrumb","pdp_url","variants","product_description","instructions","storage_instructions",
    "preparationinstructions","instructionforuse","country_of_origin","allergens","age_of_the_product","age_recommendations",
    "flavour","nutritions","nutritional_information","vitamins","labelling","grade","region","packaging","receipies",
    "processed_food","barcode","frozen","chilled","organictype","cooking_part","Handmade","max_heating_temperature",
    "special_information","label_information","dimensions","special_nutrition_purpose","feeding_recommendation","warranty",
    "color","model_number","material","usp","dosage_recommendation","tasting_note","food_preservation","size","rating",
    "review","file_name_1","image_url_1","file_name_2","image_url_2","file_name_3","image_url_3","competitor_product_key",
    "fit_guide","occasion","material_composition","style","care_instructions","heel_type","heel_height","upc","features",
    "dietary_lifestyle","manufacturer_address","importer_address","distributor_address","vinification_details","recycling_information",
    "return_address","alchol_by_volume","beer_deg","netcontent","netweight","site_shown_uom","ingredients","random_weight_flag",
    "instock","promo_limit","product_unique_key","multibuy_items_pricesingle","perfect_match","servings_per_pack","Warning",
    "suitable_for","standard_drinks","environmental","grape_variety","retail_limit"
]

RE_GRAM = re.compile(GRAMMAGE_REGEX, re.IGNORECASE)

def parse_grammage(text):
    if not text:
        return "", ""
    m = RE_GRAM.search(text)
    if not m:
        return "", ""
    qty = m.group(1).replace(",", ".")
    unit = m.group(2).lower()
    if unit == "lt":
        unit = "l"
    return qty, unit

class ParserAPI:
    def __init__(self):
        self.headers = HEADERS_PAGE
        self.src = col_source
        self.dst = col_enriched

    def fetch_products(self, count=50, offset=0):
        """Fetch products from Billa API"""
        params = {"count": count, "offset": offset}
        try:
            r = requests.get(
                "https://shop.billa.at/api/product-discovery/products",
                headers=self.headers,
                params=params,
                timeout=30
            )
            r.raise_for_status()
            return r.json().get("results", [])
        except Exception as e:
            logging.error("Failed API fetch: %s", e)
            return []

    def extract_product_data(self, product):
        d = {f: "" for f in FIELDS_126}
        d["unique_id"] = product.get("sku", "")
        d["competitor_product_key"] = d["unique_id"]
        d["product_name"] = product.get("name", "")
        d["brand"] = product.get("brand", {}).get("name", "")
        d["regular_price"] = str(product.get("price", {}).get("regular", {}).get("value", ""))
        d["currency"] = "EUR" if d.get("regular_price") else ""
        d["pdp_url"] = f"https://shop.billa.at/produkte/{product.get('slug', '')}"
        images = product.get("images", [""])
        d["image_url_1"] = images[0] if images else ""
        if d["unique_id"]:
            d["file_name_1"] = f"{d['unique_id']}_1.PNG"
        d["product_description"] = product.get("descriptionShort", "")
        d["ingredients"] = product.get("ingredients", "")
        d["allergens"] = ", ".join(product.get("allergens", []))
        d["country_of_origin"] = product.get("countryOfOrigin", "")
        d["instock"] = "TRUE" if product.get("published") else "FALSE"
        d["extraction_date"] = EXTRACTION_DATE
        d["competitor_name"] = CLIENT_NAME
        d["store_addressid"] = STORE_ID

        # Breadcrumbs / categories
        breadcrumbs = []
        for cat_list in product.get("parentCategories", []):
            for cat in cat_list:
                breadcrumbs.append(cat.get("name", ""))
        d["breadcrumb"] = " > ".join(breadcrumbs[:7])
        for i in range(7):
            d[f"producthierarchy_level{i+1}"] = breadcrumbs[i] if i < len(breadcrumbs) else ""

        # Grammage
        qty, unit = parse_grammage(d["product_name"] + " " + d.get("product_description",""))
        d["grammage_quantity"], d["grammage_unit"] = qty, unit
        return d

    def enrich_and_save(self, product):
        data = self.extract_product_data(product)
        enriched = {f: data.get(f,"") for f in FIELDS_126}
        try:
            self.dst.update_one(
                {"unique_id": enriched["unique_id"]},
                {"$set": enriched},
                upsert=True
            )
            logging.info("Saved product: %s (%s)", enriched.get("product_name"), enriched.get("unique_id"))
        except Exception as e:
            logging.error("Error saving product %s: %s", enriched.get("unique_id"), e)

    def start(self, limit=1000):
        offset = 0
        batch_size = 50
        total_fetched = 0

        logging.info("Starting full product fetch...")

        while True:
            products = self.fetch_products(count=batch_size, offset=offset)
            if not products:
                logging.info("No more products returned by API. Finished fetching.")
                break

            for prod in products:
                self.enrich_and_save(prod)
                time.sleep(REQUEST_DELAY)

            fetched_count = len(products)
            total_fetched += fetched_count
            logging.info("Fetched %s products (total %s)", fetched_count, total_fetched)

            offset += fetched_count
            if total_fetched >= limit:
                break

if __name__ == "__main__":
    parser = ParserAPI()
    parser.start(limit=2000)  # increase limit as needed
