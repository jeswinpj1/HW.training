import json
import requests
import logging
from time import sleep

logging.basicConfig(level=logging.INFO)

# -------------------------------------------------
# LOAD EXISTING PRODUCT JSON
# -------------------------------------------------
input_file = "autozone_products_20251222_121157.json"
with open(input_file, "r", encoding="utf-8") as f:
    products = json.load(f)

# -------------------------------------------------
# COLLECT SKU NUMBERS
# -------------------------------------------------
sku_numbers = [str(p["sku"]).strip() for p in products if p.get("sku")]

# -------------------------------------------------
# HEADERS
# -------------------------------------------------
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'origin': 'https://www.autozone.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.autozone.com/',
    'sales-channel': 'AZRMFWEB',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'x-requested-by': 'MF',
}

# -------------------------------------------------
# FUNCTION TO FETCH REVIEWS IN CHUNKS
# -------------------------------------------------
def fetch_reviews(sku_list, chunk_size=20, delay=1):
    all_reviews = []
    for i in range(0, len(sku_list), chunk_size):
        chunk = sku_list[i:i+chunk_size]
        sku_str = ",".join(chunk)
        url = f"https://external-api.autozone.com/sls/product/product-reviews-integration-bs/v1/review-statistics?skuNumbers={sku_str}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200 and response.text.strip():
                all_reviews.extend(response.json())
                logging.info(f"Fetched reviews for SKUs: {sku_str}")
            else:
                logging.warning(f"Failed for SKUs: {sku_str} | Status: {response.status_code}")
        except Exception as e:
            logging.error(f"Exception fetching SKUs {sku_str}: {e}")
        
        sleep(delay)  # avoid hitting the API too fast
    return all_reviews

# -------------------------------------------------
# FETCH ALL REVIEWS
# -------------------------------------------------
review_data = fetch_reviews(sku_numbers)

def safe_float(value, default=0.0):
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

# MAP REVIEW DATA TO PRODUCTS
review_map = {r["skuNumber"]: r for r in review_data}

for product in products:
    sku = str(product.get("sku"))
    review_info = review_map.get(sku)
    if review_info:
        product["averageOverallRating"] = safe_float(review_info.get("averageOverallRating"))
        product["totalReviewCount"] = safe_int(review_info.get("totalReviewCount"))
        product["reviewsOnlyCount"] = safe_int(review_info.get("reviewsOnlyCount"))
        product["recommendedCount"] = safe_int(review_info.get("recommendedCount"))
        product["notRecommendedCount"] = safe_int(review_info.get("notRecommendedCount"))
        product["recommendPercentage"] = safe_float(review_info.get("recommendPercentage"))
        product["ratingDistributionValues"] = review_info.get("ratingDistributionValues", [])


# -------------------------------------------------
# SAVE TO NEW JSON FILE
# -------------------------------------------------
output_file = "products_with_reviews.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(products, f, indent=4)

logging.info(f"✅ Enriched products saved to {output_file}")
print(f"✅ Enriched JSON saved: {output_file}")
