import requests
from parsel import Selector
from urllib.parse import urlparse
import time

BASE = "https://www.portwest.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html, */*",
    "X-Requested-With": "XMLHttpRequest",
}

INPUT_FILE = "portwest_menu_links.txt"
OUTPUT_FILE = "portwest_product_urls.txt"

all_products = set()

# ---------------------------
# Read category URLs
# ---------------------------
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    category_urls = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(category_urls)} categories")

# ---------------------------
# Process each category
# ---------------------------
for cat_url in category_urls:

    # Example path:
    # /products/footwear/X/2/5
    parts = urlparse(cat_url).path.strip("/").split("/")

    if len(parts) < 5:
        continue

    level = parts[2]        # X
    group = parts[3]        # 2
    category_id = parts[4]  # 5

    offset = 24

    while True:
        api_url = (
            f"{BASE}/products/load_more_category_products/"
            f"{level}/{group}/{category_id}/{offset}"
        )

        print(f"Fetching: {api_url}")
        r = requests.get(api_url, headers=HEADERS, timeout=30)

        if r.status_code != 200 or not r.text.strip():
            break

        sel = Selector(text=r.text)

        product_links = sel.xpath(
            '//div[contains(@class,"product")]'
            '//a[contains(@href,"/products/view")]/@href'
        ).getall()

        if not product_links:
            break

        for link in product_links:
            all_products.add(BASE + link)

        print(f"  → {len(product_links)} products")

        offset += 24
        time.sleep(0.8)

# ---------------------------
# Save output
# ---------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for url in sorted(all_products):
        f.write(url + "\n")

print(f"\nTotal unique products: {len(all_products)}")
print(f"Saved to {OUTPUT_FILE}")
