import json
import requests
from urllib.parse import urlparse
import time
from html import unescape
from re import sub

# --- Config ---
BASE_API = "https://www.sephora.sg/api/v2.6/products/"
INCLUDE_PARAMS = (
    "variants.filter_values,variants.ingredient_preference,"
    "featured_ad.virtual_bundle.bundle_elements,product_articles,filter_types" # Using INCLUDE_PARAMS, get all the variant, ingredient, bundle, article, and filter info in one API call.
)

OUTPUT_FILE = "sephora_output.json"
INPUT_FILE = "/home/user/HW.training/1sephora1_products1_tree.json"
TEST_LIMIT = 1000  # limit number of URLs for testing

# --- Headers ---
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-SG",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "x-app-platform": "web_desktop",
    "x-app-version": "1.0.0",
    "x-platform": "web",
    "x-requested-with": "XMLHttpRequest",
    "x-site-country": "SG",
    "origin": "https://www.sephora.sg",
    "referer": "https://www.sephora.sg/",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    ),
}


# --- Helper: clean HTML ---
def clean_html(text):
    if not text:
        return None
    text = unescape(text)
    text = sub("<[^<]+?>", " ", text)
    text = " ".join(text.split())
    return text.strip()


# --- Extract Product Details ---
def get_product_details(product_url):
    parsed = urlparse(product_url)
    path = parsed.path

    parts = path.strip("/").split("/")
    if len(parts) < 2:
        print(f"❌ Invalid URL format: {product_url}")
        return None

    product_slug = parts[1]
    variant_slug = parts[3] if len(parts) > 3 else None

    if variant_slug:
        api_url = f"{BASE_API}{product_slug}?v={variant_slug}&include={INCLUDE_PARAMS}"
    else:
        api_url = f"{BASE_API}{product_slug}?include={INCLUDE_PARAMS}"

    print(f"🔹 Requesting: {api_url}")
    response = requests.get(api_url, headers=HEADERS)

    if response.status_code == 422:
        print("⚠️ 422 Error, retrying without variant slug...")
        api_url = f"{BASE_API}{product_slug}?include={INCLUDE_PARAMS}"
        response = requests.get(api_url, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code} - {response.text[:200]}")
        return None

    data = response.json().get("data", {})
    attributes = data.get("attributes", {})

    # --- Price handling ---
    price_data = attributes.get("price") or {}
    if isinstance(price_data, dict):
        original_price = price_data.get("was")
        selling_price = price_data.get("now")
        promo_label = price_data.get("label")
    else:
        original_price = selling_price = price_data
        promo_label = None

    # --- Extract clean fields ---
    product = {
        "retailer_unique_id": data.get("id"),
        "retailer_name": "Sephora SG",
        "product_name": attributes.get("name"),
        "brand": attributes.get("brand", {}).get("name") if attributes.get("brand") else None,
        "grammage_quantity": attributes.get("size_value"),
        "grammage_unit": attributes.get("size_unit"),
        "original_price": original_price,
        "selling_price": selling_price,
        "promotion_description": promo_label,
        "pdp_url": f"https://www.sephora.sg{path}",
        "image_url": (attributes.get("image_urls") or [None])[0],
        "ingredients": clean_html(attributes.get("ingredients")),
        "directions": clean_html(attributes.get("how_to")),
        "disclaimer": clean_html(attributes.get("safety_warning")),
        "product_description": clean_html(attributes.get("description")),
        "product_texture": attributes.get("texture"),
        "diet_suitability": attributes.get("diet_suitability"),
        "skin_type": attributes.get("skin_type"),
        "colour": attributes.get("colour"),
        "hair_type": attributes.get("hair_type"),
        "skin_tone": attributes.get("skin_tone"),
    }

    return product


# --- Recursively Extract URLs from JSON ---
def extract_urls(obj):
    urls = []
    if isinstance(obj, dict):
        for v in obj.values():
            urls.extend(extract_urls(v))
    elif isinstance(obj, list):
        for item in obj:
            urls.extend(extract_urls(item))
    elif isinstance(obj, str) and obj.startswith("https://www.sephora.sg/products/"):
        urls.append(obj)
    return urls


# --- Main Execution ---
if __name__ == "__main__":
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    product_urls = extract_urls(data)
    total = len(product_urls)
    print(f"\n📦 Total URLs found: {total}")

    success_count = 0
    fail_count = 0
    results = []

    for idx, url in enumerate(product_urls[:TEST_LIMIT], 1):
        print(f"\n[{idx}/{TEST_LIMIT}] Processing: {url}")
        try:
            product_data = get_product_details(url)
            if product_data:
                results.append(product_data)
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"❌ Exception: {e}")
            fail_count += 1
        time.sleep(1)

    # --- Save results ---
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # --- Summary ---
    total_requests = success_count + fail_count
    success_rate = (success_count / total_requests) * 100 if total_requests else 0

    print("\n📊 SUMMARY")
    print(f"Total Requests: {total_requests}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failures: {fail_count}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"\n💾 Saved results to: {OUTPUT_FILE}")
