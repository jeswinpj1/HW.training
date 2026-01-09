import requests
from parsel import Selector
from urllib.parse import urljoin, urlparse, parse_qs

BASE = "https://www.fivebelow.com"

SUBCATEGORY_FILE = "fivebelow_subcategory_urls.txt"
OUTPUT_FILE = "fivebelow_product_urls.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_last_page(sel):
    """
    Extract last page number from pagination
    """
    last_page_url = sel.xpath(
        '//a[contains(@title,"last page")]/@href'
    ).get()

    if not last_page_url:
        return 1

    qs = parse_qs(urlparse(last_page_url).query)
    return int(qs.get("p", [1])[0])


all_products = []

with open(SUBCATEGORY_FILE, "r", encoding="utf-8") as f:
    subcategories = [line.strip() for line in f if line.strip()]

for sub_url in subcategories:
    print(f"\n📂 Sub-category: {sub_url}")

    # page 1
    resp = requests.get(sub_url, headers=HEADERS, timeout=30)
    sel = Selector(text=resp.text)

    last_page = get_last_page(sel)
    print(f"➡️ Total pages: {last_page}")

    for page in range(1, last_page + 1):
        page_url = f"{sub_url}?p={page}"
        print(f"   🔄 Page {page}: {page_url}")

        r = requests.get(page_url, headers=HEADERS, timeout=30)
        s = Selector(text=r.text)

        product_urls = s.xpath(
            '//a[contains(@class,"absolute") and contains(@class,"size-full")]/@href'
        ).getall()

        for u in product_urls:
            all_products.append(urljoin(BASE, u))


# ✅ remove duplicates, preserve order
unique_products = list(dict.fromkeys(all_products))

# ✅ save to txt
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for u in unique_products:
        f.write(u + "\n")

print("\n✅ DONE")
print(f"TOTAL PRODUCTS: {len(unique_products)}")
print(f"SAVED TO: {OUTPUT_FILE}")
