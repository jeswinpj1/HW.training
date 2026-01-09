import requests
import time
from pymongo import MongoClient
from urllib.parse import urlparse

# ----------------------------
# MONGODB
# ----------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["canadiantire"]

products_col = db["products"]
pdp_col = db["product_details"]

# ----------------------------
# PDP API
# ----------------------------
PDP_API = "https://apim.canadiantire.ca/v1/product/api/v2/product/productFamily/{}"

PARAMS = {
    "baseStoreId": "CTR",
    "lang": "en_CA",
    "storeId": "452",
    "light": "true"
}

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "bannerid": "CTR",
    "basesiteid": "CTR",
    "browse-mode": "OFF",
    "cache-control": "no-cache",
    "ocp-apim-subscription-key": "c01ef3612328420c9f5cd9277e815a0e",
    "origin": "https://www.canadiantire.ca",
    "referer": "https://www.canadiantire.ca/",
    "service-client": "ctr/web",
    "service-version": "v1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "x-web-host": "www.canadiantire.ca"
}

# ----------------------------
# UTILS
# ----------------------------
def normalize_product_code(code):
    """
    Converts:
    0850001P -> 0850001p
    """
    return code.lower()

# ----------------------------
# FETCH PDP
# ----------------------------
def fetch_pdp(product_code):
    url = PDP_API.format(product_code)
    r = requests.get(url, headers=HEADERS, params=PARAMS, timeout=30)
    r.raise_for_status()
    return r.json()

# ----------------------------
# MAIN
# ----------------------------
def crawl_pdp_from_db():

    cursor = products_col.find(
        {"product_code": {"$exists": True}},
        {"product_code": 1, "sku_id": 1, "url": 1}
    )

    for product in cursor:
        raw_code = product.get("product_code")
        if not raw_code:
            continue

        product_code = normalize_product_code(raw_code)

        print(f"Fetching PDP: {product_code}")

        try:
            data = fetch_pdp(product_code)

            pdp_doc = {
                "product_code": raw_code,
                "sku_id": product.get("sku_id"),
                "name": data.get("name"),
                "brand": data.get("brand", {}).get("label"),
                "badges": data.get("badges", []),

                "price": data.get("currentPrice", {}).get("value"),
                "original_price": data.get("originalPrice", {}).get("value"),

                "rating": data.get("rating"),
                "ratings_count": data.get("ratingsCount"),

                "breadcrumb": data.get("breadcrumbList", []),

                "short_description": data.get("shortDescription"),
                "long_description": data.get("longDescription"),

                "specifications": data.get("specifications", []),

                "images": [
                    img.get("url")
                    for img in data.get("images", [])
                    if img.get("mediaType") == "GALLERY_IMAGE"
                ],

                "videos": data.get("videoList", []),

                "fulfillment": data.get("fulfillment"),
                "availability": data.get("fulfillment", {}).get("availability"),

                "vendor": {
                    "vendorName": data.get("vendorName"),
                    "vendorNumber": data.get("vendorNumber")
                },

                "pdp_url": "https://www.canadiantire.ca" + data.get("pdpUrl", ""),
                "raw": data  # keep full response
            }

            pdp_col.update_one(
                {"product_code": raw_code},
                {"$set": pdp_doc},
                upsert=True
            )

            time.sleep(0.4)

        except Exception as e:
            print(f"❌ Failed {product_code}: {e}")

    print("✅ PDP crawling completed")

# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    crawl_pdp_from_db()
