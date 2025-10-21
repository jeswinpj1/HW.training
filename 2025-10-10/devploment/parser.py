

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Billa Austria API Scraper
# -------------------------
# - Fetches products via Billa API
# - Parses key fields
# - Saves/updates each product individually in MongoDB
# - Handles up to 352 pages
# """

# import requests
# from pymongo import MongoClient
# from datetime import datetime
# import time

# # ---------------- CONFIG ----------------
# MONGO_URI = "mongodb://localhost:27017/"
# DB_NAME = "billa_scraper126"
# DATA_COLLECTION = "12_product_data"

# COMPETITOR_NAME = "Billa"
# STORE_NAME = "Billa Online"
# COUNTRY = "Austria"

# BASE_API = "https://shop.billa.at/api/products"
# STORE_ID = "00-10"
# PAGE_SIZE = 30
# TOTAL_PAGES = 352
# REQUEST_DELAY = 1.5

# HEADERS = {
#     "accept": "application/json, text/plain, */*",
#     "accept-language": "en-US,en;q=0.9",
#     "cache-control": "no-cache",
#     "pragma": "no-cache",
#     "referer": "https://shop.billa.at/kategorie",
#     "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
# }

# # ---------------- MONGO ----------------
# mongo_client = MongoClient(MONGO_URI)
# col_data = mongo_client[DB_NAME][DATA_COLLECTION]

# # ---------------- FETCH PRODUCTS ----------------
# def fetch_products(page=0):
#     params = {
#         "sortBy": "relevance",
#         "storeId": STORE_ID,
#         "page": page,
#         "pageSize": PAGE_SIZE
#     }
#     try:
#         response = requests.get(BASE_API, headers=HEADERS, params=params, timeout=30)
#         if response.status_code != 200:
#             print(f"Error {response.status_code} on page {page}")
#             return None
#         return response.json()
#     except Exception as e:
#         print(f"Request error on page {page}: {e}")
#         return None

# # ---------------- PARSE & SAVE ----------------
# def parse_and_save(product, mongo_client):
#     """
#     Parse a single product from Billa API JSON and save to MongoDB.
#     """
#     unique_id = product.get("sku") or product.get("productId") or ""
#     product_name = product.get("name", "")
    
#     # Brand
#     brand = ""
#     if isinstance(product.get("brand"), dict):
#         brand = product["brand"].get("name", "")
    
#     # Breadcrumbs / Categories
#     breadcrumb_levels = [""] * 7
#     breadcrumbs = []
#     parent_categories = product.get("parentCategories", [])
#     if parent_categories and isinstance(parent_categories, list):
#         first_level = parent_categories[0] if isinstance(parent_categories[0], list) else parent_categories
#         for i, cat in enumerate(first_level[:7]):
#             breadcrumb_levels[i] = cat.get("name", "")
#             breadcrumbs.append(cat.get("name", ""))
    
#     # Price
#     price_info = product.get("price", {}).get("regular", {})
#     regular_price = price_info.get("value")
#     if regular_price is not None:
#         regular_price = float(regular_price) / 100 if regular_price > 10 else regular_price
#         regular_price = f"{regular_price:.2f}"
#     else:
#         regular_price = ""
    
#     # Images
#     images = product.get("images", [])
#     if isinstance(images, list) and len(images) > 0:
#         if isinstance(images[0], dict):
#             image_url_1 = images[0].get("url", "")
#         else:
#             image_url_1 = images[0]
#     else:
#         image_url_1 = ""
#     file_name_1 = f"{unique_id}_1.PNG" if unique_id else ""
    
#     # Other fields
#     data = {
#         "unique_id": unique_id,
#         "competitor_name": COMPETITOR_NAME,
#         "store_name": STORE_NAME,
#         "extraction_date": datetime.now().strftime("%Y-%m-%d"),
#         "product_name": product_name,
#         "brand": brand,
#         "producthierarchy_level1": breadcrumb_levels[0],
#         "producthierarchy_level2": breadcrumb_levels[1],
#         "producthierarchy_level3": breadcrumb_levels[2],
#         "producthierarchy_level4": breadcrumb_levels[3],
#         "producthierarchy_level5": breadcrumb_levels[4],
#         "producthierarchy_level6": breadcrumb_levels[5],
#         "producthierarchy_level7": breadcrumb_levels[6],
#         "regular_price": regular_price,
#         "currency": "EUR",
#         "breadcrumb": " > ".join(breadcrumbs),
#         "pdp_url": f"https://shop.billa.at/produkte/{product.get('slug', '')}",
#         "product_description": product.get("descriptionShort", ""),
#         "storage_instructions": product.get("storageAndUsageStatements", ""),
#         "country_of_origin": product.get("countryOfOrigin", ""),
#         "allergens": product.get("nutIngredients", ""),
#         "ingredients": product.get("ingredients", ""),
#         "image_url_1": image_url_1,
#         "file_name_1": file_name_1,
#         "netcontent": f"{product.get('amount','')} {product.get('volumeLabelShort','')}".strip()
#     }
    
#     # Save to MongoDB
#     col_data.update_one(
#         {"unique_id": unique_id},
#         {"$set": data},
#         upsert=True
#     )
    
#     print(f"Parsed & Saved: {product_name} ({unique_id})")
#     return data

# # ---------------- MAIN LOOP ----------------
# page = 0
# while page < TOTAL_PAGES:
#     result = fetch_products(page)
    
#     if not result or "results" not in result or len(result["results"]) == 0:
#         print(f"No products or failed on page {page}. Skipping...")
#         page += 1
#         time.sleep(REQUEST_DELAY)
#         continue

#     for prod in result["results"]:
#         try:
#             parse_and_save(prod, mongo_client)
#         except Exception as e:
#             print(f"Error parsing/saving product {prod.get('name','')} ({prod.get('sku','')}): {e}")

#     print(f"Completed page {page}")
#     page += 1
#     time.sleep(REQUEST_DELAY)

# print("Finished scraping all pages.")






# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Billa Austria Enrichment Script
# --------------------------------
# - Reads existing products from MongoDB
# - Visits each product PDP page to extract additional fields via XPath
# - Merges existing API data with enriched data
# - Saves to another MongoDB collection or CSV
# """

# import requests
# from pymongo import MongoClient
# from datetime import datetime
# from lxml import html
# import csv
# import time

# # ---------------- CONFIG ----------------
# MONGO_URI = "mongodb://localhost:27017/"
# DB_NAME = "billa_scraper12"
# SOURCE_COLLECTION = "product_data"
# ENRICHED_COLLECTION = "product_data_enriched"
# REQUEST_DELAY = 1.5

# HEADERS_PAGE = {
#     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
# }

# OUTPUT_FILE = f"billa_enriched_{datetime.now():%Y%m%d}.csv"

# # ---------------- MONGO ----------------
# mongo_client = MongoClient(MONGO_URI)
# col_source = mongo_client[DB_NAME][SOURCE_COLLECTION]
# col_enriched = mongo_client[DB_NAME][ENRICHED_COLLECTION]

# # ---------------- FETCH PDP HTML ----------------
# def fetch_product_page(url):
#     try:
#         res = requests.get(url, headers=HEADERS_PAGE, timeout=30)
#         if res.status_code != 200:
#             print(f"Failed to fetch PDP: {url} ({res.status_code})")
#             return None
#         return html.fromstring(res.text)
#     except Exception as e:
#         print(f"Error fetching PDP: {url} -> {e}")
#         return None

# # ---------------- EXTRACT ADDITIONAL FIELDS ----------------
# def extract_additional_fields(tree):
#     data = {}
#     if tree is None:
#         return data
    
#     try:
#         data['allergens'] = "; ".join(tree.xpath('//div[contains(@class,"ws-product-detail-row__content")]//ul/li/text()'))
#     except:
#         data['allergens'] = ""
#     try:
#         data['ingredients'] = tree.xpath(
#             'normalize-space(//div[contains(@class,"ws-product-detail-row__content")]/div[contains(text(),"Zutaten")]/following-sibling::div/text())'
#         )
#     except:
#         data['ingredients'] = ""
#     try:
#         nutrition_rows = tree.xpath('//div[contains(@class,"ws-product-detail-nutrition")]//tr')
#         nutrition_data = {}
#         for row in nutrition_rows:
#             key = row.xpath('.//th/text()')
#             value = row.xpath('.//td/text()')
#             if key and value:
#                 nutrition_data[key[0].strip()] = value[0].strip()
#         data['nutrition'] = nutrition_data
#     except:
#         data['nutrition'] = {}
    
#     print(data)
#     return data

# # ---------------- MAIN LOOP ----------------
# all_products = list(col_source.find({}))
# print(f"Loaded {len(all_products)} products from DB.")

# # Collect all fieldnames (DB fields + additional fields)
# additional_fields = ["storage_instructions", "allergens", "ingredients", "long_description", "sku", "nutrition"]
# fieldnames = list(all_products[0].keys())
# for f in additional_fields:
#     if f not in fieldnames:
#         fieldnames.append(f)

# # Open CSV file to save enriched data
# with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
#     writer.writeheader()

#     for i, product in enumerate(all_products, 1):
#         pdp_url = product.get("pdp_url")
#         tree = fetch_product_page(pdp_url)
#         extra_fields = extract_additional_fields(tree)

#         # Merge API data with enriched fields
#         enriched_data = {**product, **extra_fields}

#         # Flatten nutrition dict to string
#         if isinstance(enriched_data.get('nutrition'), dict):
#             enriched_data['nutrition'] = "; ".join(f"{k}: {v}" for k, v in enriched_data['nutrition'].items())

#         # Save to MongoDB enriched collection
#         col_enriched.update_one(
#             {"unique_id": enriched_data["unique_id"]},
#             {"$set": enriched_data},
#             upsert=True
#         )

#         # Save to CSV
#         writer.writerow(enriched_data)

#         print(f"[{i}/{len(all_products)}] Enriched: {product.get('product_name')} ({product.get('unique_id')})")
#         time.sleep(REQUEST_DELAY)

# print(f"Enrichment complete. Saved to {OUTPUT_FILE} and MongoDB collection '{ENRICHED_COLLECTION}'.")




#........................................................................................................................................................




#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Billa Austria Full Extraction Script
-----------------------------------
- Reads existing products from MongoDB
- Visits each product PDP page to extract additional fields via XPath
- Fills only the relevant fields; all other 126 fields are empty strings
- Saves to CSV and MongoDB
"""

import requests
from pymongo import MongoClient
from datetime import datetime
from lxml import html
import csv
import time

# ---------------- CONFIG ----------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "billa_scraper12"
SOURCE_COLLECTION = "product_data"
ENRICHED_COLLECTION = "full126field_product_data"
REQUEST_DELAY = 1.5

HEADERS_PAGE = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}

OUTPUT_FILE = f"billa_full_extraction_{datetime.now():%Y%m%d}.csv"

# ---------------- MONGO ----------------
mongo_client = MongoClient(MONGO_URI)
col_source = mongo_client[DB_NAME][SOURCE_COLLECTION]
col_enriched = mongo_client[DB_NAME][ENRICHED_COLLECTION]

# ---------------- FETCH PDP HTML ----------------
def fetch_product_page(url):
    try:
        res = requests.get(url, headers=HEADERS_PAGE, timeout=30)
        if res.status_code != 200:
            print(f"Failed to fetch PDP: {url} ({res.status_code})")
            return None
        return html.fromstring(res.text)
    except Exception as e:
        print(f"Error fetching PDP: {url} -> {e}")
        return None
# ---------------- EXTRACT ADDITIONAL FIELDS ----------------
def extract_additional_fields(tree):
    data = {}
    if tree is None:
        return data
    
    # Existing extraction
    try:
        data['allergens'] = "; ".join(tree.xpath('//div[contains(@class,"ws-product-detail-row__content")]//ul/li/text()'))
    except:
        data['allergens'] = ""
    try:
        data['ingredients'] = tree.xpath(
            'normalize-space(//div[contains(@class,"ws-product-detail-row__content")]/div[contains(text(),"Zutaten")]/following-sibling::div/text())'
        )
    except:
        data['ingredients'] = ""
    try:
        nutrition_rows = tree.xpath('//div[contains(@class,"ws-product-detail-nutrition")]//tr')
        nutrition_data = {}
        for row in nutrition_rows:
            key = row.xpath('.//th/text()')
            value = row.xpath('.//td/text()')
            if key and value:
                nutrition_data[key[0].strip()] = value[0].strip()
        data['nutritions'] = "; ".join(f"{k}: {v}" for k, v in nutrition_data.items())
    except:
        data['nutritions'] = ""
    
    # New XPaths integration
    xpaths = {
        "manufacturer": "//span[@class='ws-product-detail-row']//text()",
        "barcode": "//span[@class='barcode']",
        "netcontent": "//span[@class='net-content']",
        "packaging": "//span[@class='packaging']",
        "manufacturer_address": "//div[@class='ws-product-detail-row']",
        "importer_address": "//div[@class='importer-address']",
        "distributor_address": "//div[@class='ws-product-detail-row__content']",
        "care_instructions": "//div[@class='care-instructions']",
        "feeding_recommendation": "//div[@class='feeding-recommendation']",
        "dosage_recommendation": "//div[@class='dosage-recommendation']",
        "recycling_information": "//div[@class='recycling-info']",
        "environmental": "//div[@class='environmental']",
        "competitor_product_key": "//span[@class='competitor-product-key']",
        "upc": "//span[@class='upc']",
        "model_number": "//span[@class='model-number']",
        "fit_guide": "//div[@class='fit-guide']",
        "heel_height": "//span[@class='heel-height']",
        "heel_type": "//span[@class='heel-type']",
        "material": "//span[@class='material']",
        "material_composition": "//span[@class='material-composition']",
        "max_heating_temperature": "//span[@class='max-heating-temp']",
        "style": "//span[@class='style']",
        "occasion": "//span[@class='occasion']",
        "tasting_note": "//div[@class='tasting-note']",
        "vitamins": "//span[@class='vitamins']",
        "warning": "//div[@class='warning']",
        "warranties": "//div[@class='warranties']"
    }

    for field, xp in xpaths.items():
        try:
            value = tree.xpath(f'normalize-space({xp})')
            data[field] = value
        except:
            data[field] = ""
    
    return data

# ---------------- MAIN ----------------
all_products = list(col_source.find({}))
print(f"Loaded {len(all_products)} products from DB.")

# Define 126 fields in correct order, lowercase, pipe-delimited
FIELDS_126 = [
    "unique_id", "competitor_name", "store_name", "store_addressline1", "store_addressline2",
    "store_suburb", "store_state", "store_postcode", "store_addressid", "extraction_date",
    "product_name", "brand", "brand_type", "grammage_quantity", "grammage_unit", "drained_weight",
    "producthierarchy_level1", "producthierarchy_level2", "producthierarchy_level3",
    "producthierarchy_level4", "producthierarchy_level5", "producthierarchy_level6",
    "producthierarchy_level7", "regular_price", "selling_price", "price_was", "promotion_price",
    "promotion_valid_from", "promotion_valid_upto", "promotion_type", "percentage_discount",
    "promotion_description", "package_sizeof_sellingprice", "per_unit_sizedescription",
    "price_valid_from", "price_per_unit", "multi_buy_item_count", "multi_buy_items_price_total",
    "currency", "breadcrumb", "pdp_url", "variants", "product_description", "instructions",
    "storage_instructions", "preparationinstructions", "instructionforuse", "country_of_origin",
    "allergens", "age_of_the_product", "age_recommendations", "flavour", "nutritions",
    "nutritional_information", "vitamins", "labelling", "grade", "region", "packaging", "receipies",
    "processed_food", "barcode", "frozen", "chilled", "organictype", "cooking_part", "handmade",
    "max_heating_temperature", "special_information", "label_information", "dimensions",
    "special_nutrition_purpose", "feeding_recommendation", "warranty", "color", "model_number",
    "material", "usp", "dosage_recommendation", "tasting_note", "food_preservation", "size",
    "rating", "review", "file_name_1", "image_url_1", "file_name_2", "image_url_2", "file_name_3",
    "image_url_3", "competitor_product_key", "fit_guide", "occasion", "material_composition", "style",
    "care_instructions", "heel_type", "heel_height", "upc", "features", "dietary_lifestyle",
    "manufacturer_address", "importer_address", "distributor_address", "vinification_details",
    "recycling_information", "return_address", "alchol_by_volume", "beer_deg", "netcontent",
    "netweight", "site_shown_uom", "ingredients", "random_weight_flag", "instock", "promo_limit",
    "product_unique_key", "multibuy_items_pricesingle", "perfect_match", "servings_per_pack", "warning",
    "suitable_for", "standard_drinks", "environmental", "grape_variety", "retail_limit"
]

# Open CSV file
with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS_126, delimiter="|")
    writer.writeheader()

    for i, product in enumerate(all_products, 1):
        pdp_url = product.get("pdp_url")
        tree = fetch_product_page(pdp_url)
        extra_fields = extract_additional_fields(tree)

        # Merge product data with extra fields
        enriched_data = {**product, **extra_fields}

        # Flatten nutrition if needed (already handled in extract_additional_fields)

        # Ensure all 126 fields exist; missing fields as empty string
        final_row = {field: enriched_data.get(field, "") for field in FIELDS_126}

        # Save to MongoDB enriched collection
        col_enriched.update_one(
            {"unique_id": enriched_data["unique_id"]},
            {"$set": final_row},
            upsert=True
        )

        # Write CSV row
        writer.writerow(final_row)

        print(f"[{i}/{len(all_products)}] Enriched: {product.get('product_name')} ({product.get('unique_id')})")
        time.sleep(REQUEST_DELAY)

print(f"Full extraction complete. Saved to {OUTPUT_FILE} and MongoDB collection '{ENRICHED_COLLECTION}'.")
