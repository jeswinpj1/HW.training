# import requests
# import time
# from pymongo import MongoClient

# # ----------------------------
# # MONGODB SETUP
# # ----------------------------
# client = MongoClient("mongodb://localhost:27017")
# db = client["canadiantire"]
# products_col = db["products"]
# meta_col = db["metadata"]

# # ----------------------------
# # API SETUP
# # ----------------------------
# API_URL = "https://apim.canadiantire.ca/v1/search/v2/search"

# HEADERS = {
#     'accept': 'application/json, text/plain, */*',
#     'accept-language': 'en-US,en;q=0.9',
#     'ad-info': 'true',
#     'bannerid': 'CTR',
#     'basesiteid': 'CTR',
#     'browse-mode': 'OFF',
#     'cache-control': 'no-cache',
#     'categorycode': 'DC0000006',
#     'categorylevel': 'ast-id-level-1',
#     'count': '100',
#     'cr-spa-number': '4',
#     'cr-spa-positions': '1,2,3,4',
#     'criteocategorycode': 'DC0000006',
#     'devicetype': 'd',
#     'experience': 'category',
#     'injectsponsoredproducts': 'true',
#     'lang': 'en_CA',
#     'light': 'true',
#     'ocp-apim-subscription-key': 'c01ef3612328420c9f5cd9277e815a0e',
#     'origin': 'https://www.canadiantire.ca',
#     'pagetype': 'categorylevelN',
#     'referer': 'https://www.canadiantire.ca/',
#     'service-client': 'ctr/web',
#     'service-version': 'v1',
#     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64)',
#     'x-web-host': 'www.canadiantire.ca'
# }

# PARAMS = {
#     "store": "452"
# }

# # ----------------------------
# # FETCH FUNCTION
# # ----------------------------
# def fetch_page(page):
#     PARAMS["page"] = page
#     response = requests.get(API_URL, headers=HEADERS, params=PARAMS, timeout=30)
#     response.raise_for_status()
#     return response.json()

# # ----------------------------
# # MAIN CRAWLER
# # ----------------------------
# def crawl_all():
#     page = 1

#     while True:
#         print(f"Fetching page {page}")
#         data = fetch_page(page)

#         # ----------------------------
#         # SAVE METADATA ONCE
#         # ----------------------------
#         if page == 1:
#             meta_col.update_one(
#                 {"type": "category_meta"},
#                 {"$set": {
#                     "resultCount": data.get("resultCount"),
#                     "categoryMap": data.get("metadata", {}).get("categoryMap"),
#                     "facets": data.get("facets")
#                 }},
#                 upsert=True
#             )

#         pagination = data.get("pagination", {})
#         total_pages = pagination.get("total")

#         # ----------------------------
#         # EXTRACT PRODUCTS
#         # ----------------------------
#         for p in data.get("products", []):

#             # ✅ SAFE price handling
#             price_obj = p.get("currentPrice") or {}

#             product_doc = {
#                 "sku_id": p.get("skuId"),
#                 "product_code": p.get("code"),
#                 "title": p.get("title"),
#                 "brand": p.get("brand", {}).get("label"),

#                 "price": price_obj.get("value"),
#                 "min_price": price_obj.get("minPrice"),
#                 "max_price": price_obj.get("maxPrice"),

#                 "ratings_count": p.get("ratingsCount"),
#                 "is_multisku": p.get("isMultiSku"),
#                 "bid": p.get("bid"),
#                 "sponsored": bool(p.get("sponsored")),
#                 "url": "https://www.canadiantire.ca" + p.get("url", ""),
#                 "images": [img.get("url") for img in p.get("images", [])],
#                 "skus": [sku.get("code") for sku in p.get("skus", [])],
#                 "category_code": "DC0000006",
#                 "page": page
#             }

#             # Optional safety check
#             if not product_doc["sku_id"]:
#                 continue

#             products_col.update_one(
#                 {"sku_id": product_doc["sku_id"]},
#                 {"$set": product_doc},
#                 upsert=True
#             )

#         if page >= total_pages:
#             break

#         page += 1
#         time.sleep(0.5)

#     print("Crawling completed")

# # ----------------------------
# # RUN
# # ----------------------------
# if __name__ == "__main__":
#     crawl_all()






import requests
import time
from pymongo import MongoClient

# ----------------------------
# MONGODB SETUP
# ----------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["canadiantire"]

products_col = db["products"]
meta_col = db["metadata"]

# ----------------------------
# API SETUP
# ----------------------------
API_URL = "https://apim.canadiantire.ca/v1/search/v2/search"

BASE_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'ad-info': 'true',
    'bannerid': 'CTR',
    'basesiteid': 'CTR',
    'browse-mode': 'OFF',
    'cache-control': 'no-cache',
    'categorylevel': 'ast-id-level-1',
    'count': '100',
    'cr-spa-number': '4',
    'cr-spa-positions': '1,2,3,4',
    'devicetype': 'd',
    'experience': 'category',
    'injectsponsoredproducts': 'true',
    'lang': 'en_CA',
    'light': 'true',
    'ocp-apim-subscription-key': 'c01ef3612328420c9f5cd9277e815a0e',
    'origin': 'https://www.canadiantire.ca',
    'pagetype': 'categorylevelN',
    'referer': 'https://www.canadiantire.ca/',
    'service-client': 'ctr/web',
    'service-version': 'v1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64)',
    'x-web-host': 'www.canadiantire.ca'
}

PARAMS = {
    "store": "452"
}

# ----------------------------
# FETCH FUNCTION
# ----------------------------
def fetch_page(category_code, page):
    headers = BASE_HEADERS.copy()
    headers["categorycode"] = category_code
    headers["criteocategorycode"] = category_code

    PARAMS["page"] = page

    r = requests.get(API_URL, headers=headers, params=PARAMS, timeout=30)
    r.raise_for_status()
    return r.json()

# ----------------------------
# MAIN CRAWLER
# ----------------------------
def crawl_all_categories():

    # Load categoryMap from DB
    meta = meta_col.find_one({"type": "category_meta"})
    category_map = meta.get("categoryMap", {})

    for category_code, category_name in category_map.items():
        print(f"\n▶ Crawling category: {category_name} ({category_code})")

        page = 1

        while True:
            print(f"  Fetching page {page}")
            data = fetch_page(category_code, page)

            pagination = data.get("pagination", {})
            total_pages = pagination.get("total", 1)

            for p in data.get("products", []):

                # Skip invalid/sponsored placeholders
                if not p.get("skuId"):
                    continue

                price_obj = p.get("currentPrice") or {}

                product_doc = {
                    "sku_id": p.get("skuId"),
                    "product_code": p.get("code"),
                    "title": p.get("title"),
                    "brand": p.get("brand", {}).get("label"),

                    "price": price_obj.get("value"),
                    "min_price": price_obj.get("minPrice"),
                    "max_price": price_obj.get("maxPrice"),

                    "ratings_count": p.get("ratingsCount"),
                    "is_multisku": p.get("isMultiSku"),
                    "bid": p.get("bid"),
                    "sponsored": bool(p.get("sponsored")),

                    "url": (
                        "https://www.canadiantire.ca" + p.get("url", "")
                        if p.get("url", "").startswith("/")
                        else p.get("url")
                    ),

                    "images": [img.get("url") for img in p.get("images", [])],
                    "skus": [sku.get("code") for sku in p.get("skus", [])],

                    "category_code": category_code,
                    "category_name": category_name,
                    "page": page
                }

                products_col.update_one(
                    {"sku_id": product_doc["sku_id"]},
                    {"$set": product_doc},
                    upsert=True
                )

            if page >= total_pages:
                break

            page += 1
            time.sleep(0.5)

        print(f"✔ Finished category: {category_name}")

    print("\n✅ All categories crawled successfully")

# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    crawl_all_categories()
