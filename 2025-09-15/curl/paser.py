

# import json
# import os
# import time
# import random
# from curl_cffi import requests
# from lxml import html

# # ---------------- CONFIG ---------------- #
# PROXIES = {
#     "http": "http://scraperapi.country_code=us:504eeef7c076dfcf401adae86875886d@proxy-server.scraperapi.com:8001",
#     "https": "http://scraperapi.country_code=us:504eeef7c076dfcf401adae86875886d@proxy-server.scraperapi.com:8001"
# }

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
# ]

# # ---------------- REQUEST HELPER ---------------- #
# def get_page(url, retries=3, timeout=90):
#     session = requests.Session(impersonate="chrome120")
#     session.headers.update({
#         "user-agent": random.choice(USER_AGENTS),
#         "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#     })

#     for attempt in range(retries):
#         try:
#             resp = session.get(url, proxies=PROXIES, timeout=timeout, verify=False)
#             resp.raise_for_status()
#             return resp.text
#         except requests.RequestsError as e:
#             if attempt < retries - 1:
#                 wait_time = (2 ** attempt) * 5 + random.uniform(1, 3)
#                 print(f"[RETRY] {url} failed (attempt {attempt+1}), waiting {wait_time:.1f}s...")
#                 time.sleep(wait_time)
#             else:
#                 print(f"[ERROR] {url} -> {e}")
#     return None


# # ---------------- PARSER ---------------- #
# def parse_product(url):
#     """Extract product details from a product page."""
#     page = get_page(url)
#     if not page:
#         return None

#     tree = html.fromstring(page)

#     def xp(path):
#         return tree.xpath(path)

#     product = {
#         "url": url,
#         "title": xp('//h1/text()')[0].strip() if xp('//h1/text()') else None,
#         "price": xp('//span[contains(@class,"pt-0 font-medium mr-3 text-[28px] leading-9 text-black ")]/text()')[0].strip() if xp('//span[contains(@class,"price")]/text()') else None,
#         "description": " ".join(x.strip() for x in xp('//div[contains(@class,"flex flex-col rounded-lg bg-white p-4 shadow-md")]//text()')),
#         "ingredients": " ".join(x.strip() for x in xp('//div[contains(@class,"mx-6 my-[21px] whitespace-pre-line")]//text()')),
#     }
#     return product

# # ---------------- MAIN ---------------- #
# if __name__ == "__main__":
#     # Load crawler output (categories → subcategories → products)
#     with open("cvs_output.json", "r", encoding="utf-8") as f:
#         data = json.load(f)

#     # Load existing products if cvs_products.json exists
#     all_products = []
#     processed_urls = set()
#     if os.path.exists("cvs_products.json"):
#         with open("cvs_products.json", "r", encoding="utf-8") as f:
#             all_products = json.load(f)
#             processed_urls = {p["url"] for p in all_products}
#         print(f"[INFO] Resuming... already have {len(all_products)} products")

#     failed = []

#     # Loop over product URLs from crawler
#     for subcat, urls in data.get("products", {}).items():
#         print(f"[INFO] Parsing {len(urls)} products from {subcat}")
#         for url in urls:
#             if url in processed_urls:
#                 print(f"    Skipping already parsed: {url}")
#                 continue
#             prod = parse_product(url)
#             if prod:
#                 all_products.append(prod)
#                 processed_urls.add(url)
#                 print(f"   ✔ Parsed: {prod['title']}")
#                 # Save after each product (safety in case script stops)
#                 with open("cvs_products.json", "w", encoding="utf-8") as f:
#                     json.dump(all_products, f, indent=2, ensure_ascii=False)
#             else:
#                 failed.append(url)
#             time.sleep(random.uniform(2, 5))  # throttle requests

#     if failed:
#         with open("failed_products.txt", "w", encoding="utf-8") as f:
#             f.write("\n".join(failed))

#     print(f"\n[INFO] Finished! Total saved: {len(all_products)} products. Failed: {len(failed)}")

#     # ---------------- SHOW PRODUCTS ONE BY ONE ---------------- #
#     print("\n[INFO] Showing saved products one by one...\n")
#     with open("cvs_products.json", "r", encoding="utf-8") as f:
#         products = json.load(f)

#     for idx, prod in enumerate(products, 1):
#         print("="*50)
#         print(f"Product {idx}")
#         print(f"URL: {prod.get('url')}")
#         print(f"Title: {prod.get('title')}")
#         print(f"Price: {prod.get('price')}")
#         print(f"Description: {prod.get('description')[:200]}...")
#         print(f"Ingredients: {prod.get('ingredients')}")
#         print("="*50)
#         input("Press Enter for next product...\n")




import json
import os
import time
import random
from curl_cffi import requests
from lxml import html

# ---------------- CONFIG ---------------- #
PROXIES = {
    "http": "http://scraperapi.country_code=us:504eeef7c076dfcf401adae86875886d@proxy-server.scraperapi.com:8001",
    "https": "http://scraperapi.country_code=us:504eeef7c076dfcf401adae86875886d@proxy-server.scraperapi.com:8001"
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

# ---------------- REQUEST HELPER ---------------- #
def get_page(url, retries=3, timeout=90):
    session = requests.Session(impersonate="chrome120")
    session.headers.update({
        "user-agent": random.choice(USER_AGENTS),
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    })

    for attempt in range(retries):
        try:
            resp = session.get(url, proxies=PROXIES, timeout=timeout, verify=False)
            resp.raise_for_status()
            return resp.text
        except requests.RequestsError as e:
            if attempt < retries - 1:
                wait_time = (2 ** attempt) * 5 + random.uniform(1, 3)
                print(f"[RETRY] {url} failed (attempt {attempt+1}), waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
            else:
                print(f"[ERROR] {url} -> {e}")
    return None

# ---------------- PARSER ---------------- #
def parse_product(url):
    """Extract product details from JSON-LD + HTML fallback."""
    page = get_page(url)
    if not page:
        return None

    tree = html.fromstring(page)

    # Extract JSON-LD block
    ld_json = tree.xpath('//script[@type="application/ld+json"]/text()')
    product_data = {}
    if ld_json:
        try:
            data = json.loads(ld_json[0])
            # JSON-LD can be a list
            if isinstance(data, list):
                for block in data:
                    if block.get("@type") == "Product":
                        product_data = block
                        break
            elif data.get("@type") == "Product":
                product_data = data
        except Exception as e:
            print(f"[WARN] JSON-LD parse error: {e}")

    # Parse fields
    product = {
        "url": url,
        "title": product_data.get("name"),
        "price": (product_data.get("offers") or {}).get("price"),
        "currency": (product_data.get("offers") or {}).get("priceCurrency"),
        "rating": (product_data.get("aggregateRating") or {}).get("ratingValue"),
        "reviews": (product_data.get("aggregateRating") or {}).get("reviewCount"),
        "ingredients": " ".join(x.strip() for x in tree.xpath('//div[contains(@class,"mx-6 my-[21px] whitespace-pre-line")]//text()')),
        "description": product_data.get("description"),
    }

    return product

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    with open("cvs_output.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    all_products = []
    processed_urls = set()
    if os.path.exists("cvs_products.json"):
        with open("cvs_products.json", "r", encoding="utf-8") as f:
            all_products = json.load(f)
            processed_urls = {p["url"] for p in all_products}
        print(f"[INFO] Resuming... already have {len(all_products)} products")

    failed = []

    for subcat, urls in data.get("products", {}).items():
        print(f"[INFO] Parsing {len(urls)} products from {subcat}")
        for url in urls:
            if url in processed_urls:
                print(f"    Skipping already parsed: {url}")
                continue
            prod = parse_product(url)
            if prod:
                all_products.append(prod)
                processed_urls.add(url)
                print(f"   ✔ Parsed: {prod['title']}")
                with open("cvs_products.json", "w", encoding="utf-8") as f:
                    json.dump(all_products, f, indent=2, ensure_ascii=False)
            else:
                failed.append(url)
            time.sleep(random.uniform(2, 5))

    if failed:
        with open("failed_products.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(failed))

    print(f"\n[INFO] Finished! Total saved: {len(all_products)} products. Failed: {len(failed)}")

    # ---------------- SHOW PRODUCTS ---------------- #
    print("\n[INFO] Showing saved products one by one...\n")
    with open("cvs_products.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    for idx, prod in enumerate(products, 1):
        print("="*50)
        print(f"Product {idx}")
        print(f"URL: {prod.get('url')}")
        print(f"Title: {prod.get('title')}")
        print(f"Price: {prod.get('price')} {prod.get('currency')}")
        print(f"Rating: {prod.get('rating')}")
        print(f"Reviews: {prod.get('reviews')}")
        print(f"Description: {prod.get('description')}")
        print(f"Ingredients: {prod.get('ingredients')}")
        print("="*50)
        input("Press Enter for next product...\n")
