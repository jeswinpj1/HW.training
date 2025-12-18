
import requests
import time
import json
from pymongo import MongoClient


# ==================================================
# COMMON HEADERS (USED FOR ALL APIS)
# ==================================================

COMMON_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "browse-mode": "OFF",
    "cache-control": "no-cache",
    "ocp-apim-subscription-key": "c01ef3612328420c9f5cd9277e815a0e",
    "origin": "https://www.canadiantire.ca",
    "referer": "https://www.canadiantire.ca/",
    "service-client": "ctr/web",
    "service-version": "v1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "x-web-host": "www.canadiantire.ca",
}

# ==================================================
# -------------------- CRAWLER ---------------------
# ==================================================

SEARCH_API = "https://apim.canadiantire.ca/v1/search/v2/search"

SEARCH_PARAMS = {
    "store": STORE_ID,
    "page": 1
}


def crawl_category(category_code, category_name):
    """
    Crawls one category using PLP Search API
    """
    page = 1

    while True:
        headers = COMMON_HEADERS.copy()
        headers.update({
            "categorycode": category_code,
            "criteocategorycode": category_code,
            "experience": "category",
            "pagetype": "categorylevelN",
            "light": "true",
            "count": "100",
        })

        SEARCH_PARAMS["page"] = page

        r = requests.get(SEARCH_API, headers=headers, params=SEARCH_PARAMS, timeout=30)
        r.raise_for_status()
        data = r.json()

        for p in data.get("products", []):
            if not p.get("skuId"):
                continue

            product_doc = {
                "sku_id": p.get("skuId"),
                "product_code": p.get("code"),
                "title": p.get("title"),
                "brand": p.get("brand", {}).get("label"),
                "price": (p.get("currentPrice") or {}).get("value"),
                "ratings_count": p.get("ratingsCount"),
                "sponsored": bool(p.get("sponsored")),
                "url": "https://www.canadiantire.ca" + p.get("url", ""),
                "images": [i.get("url") for i in p.get("images", [])],
                "category_code": category_code,
                "category_name": category_name,
                "page": page,
            }

            products_col.update_one(
                {"sku_id": product_doc["sku_id"]},
                {"$set": product_doc},
                upsert=True
            )

        total_pages = data.get("pagination", {}).get("total", 1)
        if page >= total_pages:
            break

        page += 1
        time.sleep(0.5)


# ==================================================
# --------------------- PARSER ---------------------
# ==================================================

PDP_API = "https://apim.canadiantire.ca/v1/product/api/v2/product/productFamily/{}"

PDP_PARAMS = {
    "baseStoreId": BASE_SITE,
    "lang": LANG,
    "storeId": STORE_ID,
    "light": "true"
}


def normalize_code(code: str) -> str:# It normalizes a product code by converting it to lowercase.collected as 10002930P > 10002930p
    return code.lower()


def parse_pdp(product_code, sku_id):
    """
    Fetches and parses PDP data using Product Family API
    """
    url = PDP_API.format(normalize_code(product_code))

    r = requests.get(url, headers=COMMON_HEADERS, params=PDP_PARAMS, timeout=30)
    r.raise_for_status()
    data = r.json()

    pdp_doc = {
        "product_code": product_code,
        "sku_id": sku_id,
        "name": data.get("name"),
        "brand": data.get("brand", {}).get("label"),
        "price": data.get("currentPrice", {}).get("value"),
        "original_price": data.get("originalPrice", {}).get("value"),
        "rating": data.get("rating"),
        "ratings_count": data.get("ratingsCount"),
        "breadcrumb": data.get("breadcrumbList"),
        "short_description": data.get("shortDescription"),
        "long_description": data.get("longDescription"),
        "specifications": data.get("specifications"),
        "images": [
            img.get("url")
            for img in data.get("images", [])
            if img.get("mediaType") == "GALLERY_IMAGE"
        ],
        "availability": data.get("fulfillment", {}).get("availability"),
        "vendor": {
            "vendorName": data.get("vendorName"),
            "vendorNumber": data.get("vendorNumber"),
        },
        "pdp_url": "https://www.canadiantire.ca" + data.get("pdpUrl", ""),
        "raw": data
    }

    pdp_col.update_one(
        {"product_code": product_code},
        {"$set": pdp_doc},
        upsert=True
    )


# ==================================================
# ------------------- FINDINGS ---------------------
# ==================================================
"""
FINDINGS
--------
 No individual review text
"""

