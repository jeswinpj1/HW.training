import requests
from parsel import Selector
from urllib.parse import urljoin

BASE = "https://www.fivebelow.com"

CATEGORY_URLS = [
    "https://www.fivebelow.com/categories/candy",
    "https://www.fivebelow.com/categories/toys-and-games",
]

OUTPUT_FILE = "fivebelow_subcategory_urls.txt"

headers = {
    "User-Agent": "Mozilla/5.0"
}

all_subcats = []

for cat_url in CATEGORY_URLS:
    print(f"Scraping: {cat_url}")

    resp = requests.get(cat_url, headers=headers, timeout=30)
    sel = Selector(text=resp.text)

    sub_urls = sel.xpath(
        '//a[contains(@class,"inline-block") '
        'and contains(@class,"cursor-pointer")]/@href'
    ).getall()

    for u in sub_urls:
        full = urljoin(BASE, u)
        all_subcats.append(full)

# ✅ remove duplicates + preserve order
unique_subcats = list(dict.fromkeys(all_subcats))

# ✅ save to txt (one per line)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for u in unique_subcats:
        f.write(u + "\n")

print(f"\nTOTAL SUB-CATEGORIES: {len(unique_subcats)}")
print(f"SAVED TO: {OUTPUT_FILE}")
