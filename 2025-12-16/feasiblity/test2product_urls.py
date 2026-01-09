import json
import time
import os
import requests
from parsel import Selector
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -------------------------
# SESSION WITH RETRIES
# -------------------------
session = requests.Session()

retries = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET","POST"]
)

adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
    "Connection": "keep-alive",
}

INPUT_FILE = "homedepot_ca_full_category_tree.json"
OUTPUT_FILE = "homedepot_ca_product_urls.json"

visited_pages = set()
product_urls = set()


# -------------------------
# LOAD EXISTING OUTPUT
# -------------------------
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        try:
            product_urls = set(json.load(f))
            print(f"🔄 Resuming with {len(product_urls)} existing URLs")
        except Exception:
            product_urls = set()


# -------------------------
# SAVE SINGLE PRODUCT URL
# -------------------------
def save_product_url(url):
    if url in product_urls:
        return

    product_urls.add(url)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(product_urls), f, indent=2, ensure_ascii=False)

    print(f"✅ Saved product: {url}")


# -------------------------
# EXTRACT PRODUCTS FROM JSON-LD
# -------------------------
def extract_products_from_jsonld(html):
    sel = Selector(text=html)
    urls = []

    for script in sel.xpath('//script[@type="application/ld+json"]/text()').getall():
        try:
            data = json.loads(script)

            offers = (
                data.get("mainEntity", {})
                    .get("offers", {})
                    .get("itemOffered", [])
            )

            if isinstance(offers, list):
                for p in offers:
                    url = p.get("url")
                    if url:
                        urls.append(url)

        except Exception:
            continue

    return urls


# -------------------------
# PAGINATION
# -------------------------
def extract_pagination_links(base_url, html):
    sel = Selector(text=html)
    links = sel.xpath(
        '//a[contains(@class,"acl-pagination__item--link")]/@href'
    ).getall()

    return {urljoin(base_url, l) for l in links}


# -------------------------
# CRAWL CATEGORY
# -------------------------
def crawl_category(start_url):
    queue = {start_url}

    while queue:
        url = queue.pop()

        if url in visited_pages:
            continue

        visited_pages.add(url)
        print(f"Fetching: {url}")

        try:
            r = session.get(
                url,
                headers=HEADERS,
                timeout=(10, 45)
            )

            if r.status_code != 200:
                print(f"Non-200: {r.status_code}")
                continue

            html = r.text

            # PRODUCTS (SAVE ONE BY ONE)
            for u in extract_products_from_jsonld(html):
                save_product_url(u)

            # PAGINATION
            for p in extract_pagination_links(url, html):
                if p not in visited_pages:
                    queue.add(p)

            time.sleep(1.5)

        except requests.exceptions.ReadTimeout:
            print("⚠️ Read timeout – skipping page")
        except Exception as e:
            print(f"Error: {e}")


# -------------------------
# MAIN
# -------------------------
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    categories = json.load(f)

for item in categories:
    cat_url = item.get("subcategory_url") or item.get("category_url")
    if cat_url:
        crawl_category(cat_url)

print(f"\n🎯 DONE")
print(f"📦 Total products saved: {len(product_urls)}")
print(f"📁 Output file: {OUTPUT_FILE}")
