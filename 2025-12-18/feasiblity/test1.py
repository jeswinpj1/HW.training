# import requests
# from pymongo import MongoClient
# import time

# # -------------------------------
# # MongoDB Setup
# # -------------------------------
# client = MongoClient("mongodb://localhost:27017")
# db = client["biggestbook"]
# collection = db["products"]

# # -------------------------------
# # API & Headers
# # -------------------------------
# url = "https://api.essendant.com/digital/digitalservices/search/v2/search"
# headers = {
#     'Accept': 'application/json, text/plain, */*',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Cache-Control': 'no-cache',
#     'Connection': 'keep-alive',
#     'Origin': 'https://www.biggestbook.com',
#     'Pragma': 'no-cache',
#     'Referer': 'https://www.biggestbook.com/',
#     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
#     'X-API-KEY': '31BC6E02FD51DF7F7CE37186A31EE9B9DEF9C642526BC29F8201D81B669B9',
# }

# # -------------------------------
# # Step 1: Get all category IDs
# # -------------------------------
# params = {
#     'fc': '0',  # fc=0 to get top-level categories (or first call)
#     'cr': 1,
#     'rs': 1,  # just need facets, one result is enough
#     'st': 'BM',
#     'cmt': 'ALT',
#     'vc': 'n',
# }

# response = requests.get(url, headers=headers, params=params, timeout=20)
# response.raise_for_status()
# data = response.json()

# # extract category values
# categories = data.get('searchResult', {}).get('appliedFacets', [])
# category_values = []

# for facet in categories:
#     if facet.get('name') == "Category":
#         for val in facet.get('values', []):
#             category_values.append({
#                 'id': val.get('id'),
#                 'description': val.get('description'),
#                 'value': val.get('value')
#             })

# print(f"Found {len(category_values)} categories.")

# # -------------------------------
# # Step 2: Loop through categories
# # -------------------------------
# rs = 24  # results per page

# for cat in category_values:
#     fc = cat['id']  # use id as fc for category
#     print(f"\nFetching category: {cat['description']} (fc={fc})")
#     cr = 1

#     while True:
#         params = {
#             'fc': fc,
#             'cr': cr,
#             'rs': rs,
#             'st': 'BM',
#             'cmt': 'ALT',
#             'vc': 'n',
#         }

#         response = requests.get(url, headers=headers, params=params, timeout=20)
#         response.raise_for_status()
#         data = response.json()

#         products = data.get('searchResult', {}).get('products', [])
#         page_context = data.get('searchResult', {}).get('pageContext', {})
#         available_results = page_context.get('availableResults', 0)

#         if not products:
#             break

#         # Normalize & Save to MongoDB
#         for p in products:
#             item = {
#                 "win": p.get("win"),
#                 "mpn": p.get("mpn"),
#                 "mfg": p.get("mfg"),
#                 "manufacturer": p.get("manufacturer"),
#                 "brand_id": p.get("brand", {}).get("id"),
#                 "brand_name": p.get("brand", {}).get("description"),
#                 "description": p.get("description"),
#                 "actual_price": p.get("actualPrice"),
#                 "list_price": p.get("listPrice"),
#                 "uom": p.get("uom"),
#                 "weight": p.get("weight"),
#                 "weight_unit": p.get("weightUnit"),
#                 "unspsc": p.get("unspsc"),
#                 "product_class": p.get("productClass"),
#                 "stocking_indicator": p.get("stockingIndicator"),
#                 "discontinued": p.get("discontinued"),
#                 "image_url": p.get("image", {}).get("url"),
#                 "more_images": [img.get("url") for img in p.get("moreImages", [])],
#                 "selling_points": p.get("sellingPoints", []),
#                 "category_id": fc,
#                 "category_name": cat['description'],
#                 "raw": p,
#             }
#             if item["win"]:
#                 collection.update_one({"win": item["win"]}, {"$set": item}, upsert=True)

#         print(f"Saved {len(products)} products from {cat['description']}, CR={cr}")

#         # Pagination
#         cr += rs
#         if cr > available_results:
#             break

#         time.sleep(0.5)  # polite delay

# print("\nAll categories processed.")
# client.close()





import requests
from pymongo import MongoClient
import time

# -------------------------------
# MongoDB Setup
# -------------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["biggestbook"]
collection = db["products"]

# -------------------------------
# API & Headers
# -------------------------------
url = "https://api.essendant.com/digital/digitalservices/search/v2/search"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Origin': 'https://www.biggestbook.com',
    'Pragma': 'no-cache',
    'Referer': 'https://www.biggestbook.com/',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'X-API-KEY': '31BC6E02FD51DF7F7CE37186A31EE9B9DEF9C642526BC29F8201D81B669B9',
}

# -------------------------------
# Helper: Fetch with retries
# -------------------------------
def fetch_with_retry(params, retries=5, delay=5, timeout=60):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed for CR={params.get('cr')}: {e}")
            time.sleep(delay)
    print(f"Failed to fetch CR={params.get('cr')} after {retries} retries.")
    return None

# -------------------------------
# Step 1: Get all category IDs
# -------------------------------
params = {'fc': '0', 'cr': 1, 'rs': 1, 'st': 'BM', 'cmt': 'ALT', 'vc': 'n'}
data = fetch_with_retry(params)
category_values = []

if data:
    categories = data.get('searchResult', {}).get('appliedFacets', [])
    for facet in categories:
        if facet.get('name') == "Category":
            for val in facet.get('values', []):
                category_values.append({
                    'id': val.get('id'),
                    'description': val.get('description') or "Unknown",
                    'value': val.get('value')
                })

print(f"Found {len(category_values)} categories.")

# -------------------------------
# Step 2: Loop through categories
# -------------------------------
rs = 24
for cat in category_values:
    fc = cat['id']
    category_name = cat.get('description', 'Unknown')
    print(f"\nFetching category: {category_name} (fc={fc})")
    cr = 1

    while True:
        params = {'fc': fc, 'cr': cr, 'rs': rs, 'st': 'BM', 'cmt': 'ALT', 'vc': 'n'}
        data = fetch_with_retry(params)
        if not data:
            break

        products = data.get('searchResult', {}).get('products', [])
        page_context = data.get('searchResult', {}).get('pageContext', {})
        available_results = page_context.get('availableResults', 0)

        if not products:
            break

        # Normalize & save to MongoDB
        for p in products:
            item = {
                "win": p.get("win"),
                "mpn": p.get("mpn"),
                "mfg": p.get("mfg"),
                "manufacturer": p.get("manufacturer"),
                "brand_id": p.get("brand", {}).get("id"),
                "brand_name": p.get("brand", {}).get("description"),
                "description": p.get("description"),
                "actual_price": p.get("actualPrice"),
                "list_price": p.get("listPrice"),
                "uom": p.get("uom"),
                "weight": p.get("weight"),
                "weight_unit": p.get("weightUnit"),
                "unspsc": p.get("unspsc"),
                "product_class": p.get("productClass"),
                "stocking_indicator": p.get("stockingIndicator"),
                "discontinued": p.get("discontinued"),
                "image_url": p.get("image", {}).get("url"),
                "more_images": [img.get("url") for img in p.get("moreImages", [])],
                "selling_points": p.get("sellingPoints", []),
                "category_id": fc,
                "category_name": category_name,
                "raw": p,
            }
            if item["win"]:
                collection.update_one({"win": item["win"]}, {"$set": item}, upsert=True)

        print(f"Saved {len(products)} products from {category_name}, CR={cr}")

        cr += rs
        if cr > available_results:
            break

        time.sleep(0.5)

print("\nAll categories processed.")
client.close()
