# import requests
# from parsel import Selector

# BASE_URL = "https://www.walmart.com"
# INPUT_FILE = "/home/user/HW.training/walmart_filtered_subcategories.txt"
# OUTPUT_FILE = "/home/user/HW.training/walmart_subsubcategories.txt"

# headers = {
#     "authority": "www.walmart.com",
#     "method": "GET",
#     "scheme": "https",
#     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#     "accept-language": "en-US,en;q=0.9",
#     "accept-encoding": "gzip, deflate, br, zstd",
#     "cache-control": "no-cache",
#     "pragma": "no-cache",
#     "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": '"Linux"',
#     "sec-fetch-dest": "document",
#     "sec-fetch-mode": "navigate",
#     "sec-fetch-site": "none",
#     "sec-fetch-user": "?1",
#     "upgrade-insecure-requests": "1",
#     "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
# }

# # Read subcategory URLs from file
# with open(INPUT_FILE, "r") as f:
#     subcategory_urls = [line.strip() for line in f if line.strip()]

# print(f"Total subcategory URLs to process: {len(subcategory_urls)}")

# subsub_links = []

# for url in subcategory_urls:
#     try:
#         resp = requests.get(url, headers=headers)
#         sel = Selector(text=resp.text)

#         # XPath: select <a> with the exact class
#         links = sel.xpath(
#             '//a[contains(@class, "no-underline sans-serif flex flex-column items-center")]/@href'
#         ).getall()
#         links = [link if link.startswith("http") else BASE_URL + link for link in links]
#         subsub_links.extend(links)

#         print(f"Collected {len(links)} sub-sub-category links from {url}")

#     except Exception as e:
#         print(f"Error fetching {url}: {e}")

# # Deduplicate
# subsub_links = list(set(subsub_links))

# # Save to file
# with open(OUTPUT_FILE, "w") as f:
#     for link in subsub_links:
#         f.write(link + "\n")

# print(f"\nTotal sub-sub-category links collected: {len(subsub_links)}")
# print(f"Saved to {OUTPUT_FILE}")




#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  sub and sub sub category urls code ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#



import requests
import json
import time
from parsel import Selector
from urllib.parse import urljoin

INPUT_FILE = "/home/user/HW.training/walmart_subsubcategories.txt"
OUTPUT_FILE = "/home/user/HW.training/walmart_products.json"

BASE = "https://www.walmart.com"

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br, zstd",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
}


# ===========================
# EXTRACTORS
# ===========================

def extract_products_from_next_data(sel):
    """Primary extractor for modern Walmart pages"""
    products = set()

    data = sel.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
    if not data:
        return products

    try:
        js = json.loads(data)

        def walk(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in ("canonicalUrl", "productPageUrl", "seoUrl"):
                        if isinstance(v, str) and "/ip/" in v:
                            products.add(urljoin(BASE, v.split("?")[0]))
                    walk(v)
            elif isinstance(obj, list):
                for i in obj:
                    walk(i)

        walk(js)
    except Exception:
        pass

    return products


def extract_products_from_html(sel):
    """Fallback HTML extractor"""
    products = set()
    links = sel.xpath('//main//a[contains(@href,"/ip/")]/@href').getall()

    for link in links:
        products.add(urljoin(BASE, link.split("?")[0]))

    return products


def extract_products_from_jsonld(sel):
    """Legacy fallback"""
    products = set()
    scripts = sel.xpath('//script[@type="application/ld+json"]/text()').getall()

    for s in scripts:
        try:
            data = json.loads(s)
            if isinstance(data, dict) and data.get("@type") == "CollectionPage":
                itemlist = data.get("mainEntity", {})
                if itemlist.get("@type") == "ItemList":
                    for item in itemlist.get("itemListElement", []):
                        url = item.get("url")
                        if url and "/ip/" in url:
                            products.add(urljoin(BASE, url))
        except Exception:
            pass

    return products


# ===========================
# SCRAPER
# ===========================

def scrape_category(url, max_pages=30):
    page = 1
    all_products = set()

    while page <= max_pages:
        sep = "&" if "?" in url else "?"
        paged_url = f"{url}{sep}page={page}" if page > 1 else url

        print(f"   → Page {page}")
        resp = requests.get(paged_url, headers=HEADERS, timeout=30)

        if resp.status_code != 200:
            break

        sel = Selector(text=resp.text)

        page_products = set()

        # 1️⃣ PRIMARY
        page_products |= extract_products_from_next_data(sel)

        # 2️⃣ HTML fallback
        if not page_products:
            page_products |= extract_products_from_html(sel)

        # 3️⃣ JSON-LD fallback
        if not page_products:
            page_products |= extract_products_from_jsonld(sel)

        # STOP condition (true end)
        if not page_products:
            print("     ⛔ No products on page → stopping")
            break

        all_products |= page_products
        page += 1
        time.sleep(1)

    return all_products


# ===========================
# MAIN
# ===========================

with open(INPUT_FILE) as f:
    category_urls = [line.strip() for line in f if line.strip()]

print(f"Total category URLs: {len(category_urls)}")

final_products = set()

for idx, cat_url in enumerate(category_urls, 1):
    print(f"\n[{idx}/{len(category_urls)}] Scraping: {cat_url}")
    try:
        products = scrape_category(cat_url)
        print(f"   ✔ Products found: {len(products)}")
        final_products |= products
    except Exception as e:
        print(f"   ❌ Error: {e}")

print(f"\nTOTAL UNIQUE PRODUCTS: {len(final_products)}")

# Save JSON
output = {
    "total_products": len(final_products),
    "products": sorted(final_products)
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(output, f, indent=2)

print(f"Saved → {OUTPUT_FILE}")

