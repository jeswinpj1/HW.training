import requests
import json
import time
from urllib.parse import urlparse, parse_qs

# ---------- CONFIG ----------
URLS_FILE = "targus_grandchild_urls.txt"  # your saved URLs
OUTPUT_FILE = "targus_products.json"
STORE_ID = "7553024066"
PRODUCTS_PER_PAGE = 63
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "origin": "https://eu.targus.com",
    "pragma": "no-cache",
    "referer": "https://eu.targus.com/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
}

# ---------- FUNCTIONS ----------
def extract_category_id(url):
    """Extract category_id from a saved URL query or path"""
    # if your URLs already contain category_id in query params, extract it
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if "category_id" in qs:
        return qs["category_id"][0]
    # fallback: try to extract from URL path numbers
    parts = parsed.path.strip("/").split("-")
    for p in parts:
        if p.isdigit():
            return p
    return None

def fetch_products(category_id):
    """Fetch all products for a category using pagination"""
    page_num = 1
    while True:
        api_url = (
            f"https://api.fastsimon.com/categories_navigation"
            f"?request_source=v-next&src=v-next&UUID=8fb07dc3-f0b7-4ea1-bc29-4286c08e8c3f"
            f"&uuid=8fb07dc3-f0b7-4ea1-bc29-4286c08e8c3f&store_id={STORE_ID}"
            f"&api_type=json&category_id={category_id}&facets_required=1"
            f"&products_per_page={PRODUCTS_PER_PAGE}&page_num={page_num}&with_product_attributes=true&qs=false"
        )

        resp = requests.get(api_url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print(f"[ERROR] Failed to fetch page {page_num} for category {category_id}")
            break

        data = resp.json()
        items = data.get("items", [])
        if not items:
            break  # no more products

        for item in items:
            save_product(item)

        print(f"Saved {len(items)} products from page {page_num} (category {category_id})")
        page_num += 1
        time.sleep(0.5)  # be polite

def save_product(product):
    """Append a single product to JSON file"""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        json.dump(product, f, ensure_ascii=False)
        f.write("\n")  # each product on a new line

# ---------- MAIN ----------
with open(URLS_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Found {len(urls)} category URLs.")

for url in urls:
    category_id = extract_category_id(url)
    if category_id:
        print(f"Fetching products for category_id={category_id} ...")
        fetch_products(category_id)
    else:
        print(f"[WARNING] Could not extract category_id from URL: {url}")
