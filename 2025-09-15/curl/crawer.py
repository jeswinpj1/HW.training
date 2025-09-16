



# import json
# from curl_cffi import requests
# from lxml import html

# BASE_URL = "https://www.cvs.com/shop"

# PROXIES = {
#     "http": "http://scraperapi.country_code=us:504eeef7c076dfcf401adae86875886d@proxy-server.scraperapi.com:8001",
#     "https": "http://scraperapi.country_code=us:504eeef7c076dfcf401adae86875886d@proxy-server.scraperapi.com:8001"
# }

# # Chrome 120 impersonation
# session = requests.Session(impersonate="chrome120")

# # Headers
# session.headers.update({
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#                   "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
# })

# # Example cookies
# session.cookies.set("cvs_locale", "en_US")
# session.cookies.set("aka_debug", "1")


# def get_page(url):
#     """Fetch page HTML with proxy and error handling."""
#     try:
#         resp = session.get(url, proxies=PROXIES, timeout=30, verify=False)
#         resp.raise_for_status()
#         return resp.text
#     except Exception as e:
#         print(f"[ERROR] Failed to fetch {url} -> {e}")
#         return None


# def get_categories():
#     """Extract category URLs."""
#     page = get_page(BASE_URL)
#     if not page:
#         return []
#     tree = html.fromstring(page)
#     categories = tree.xpath('//a[@class="contentful link-group-anchor"]/@href')
#     return [href if href.startswith("http") else BASE_URL.rstrip("/") + href for href in categories]


# def get_subcategories(cat_url):
#     """Extract subcategory URLs from a category."""
#     page = get_page(cat_url)
#     if not page:
#         return []
#     tree = html.fromstring(page)
#     subcats = tree.xpath('//a[@class="pulse-text-black pulse-link viz-nav-cta-text"]/@href')
#     return [href if href.startswith("http") else BASE_URL.rstrip("/") + href for href in subcats]


# def get_products(subcat_url):
#     """Extract product URLs from a subcategory."""
#     page = get_page(subcat_url)
#     if not page:
#         return []
#     tree = html.fromstring(page)
#     # products = tree.xpath('//a[contains(@href,"/product/")]/@href')
#     products = tree.xpath('//a[@class="css-1dbjc4n r-1p0dtai r-1loqt21 r-1d2f490 r-u8s1d r-zchlnj r-ipm5af r-1otgn73 r-1i6wzkk r-lrvibr"]/@href')

#     return [href if href.startswith("http") else BASE_URL.rstrip("/") + href for href in products]


# if __name__ == "__main__":
#     output = {"categories": [], "subcategories": {}, "products": {}}

#     print("[INFO] Fetching categories...")
#     categories = get_categories()
#     output["categories"] = categories
#     print(f"[INFO] Found {len(categories)} categories")

#     # Limit for testing (change/remove later)
#     for cat in categories[:3]:
#         print(f"[INFO] Crawling category: {cat}")
#         subcats = get_subcategories(cat)
#         output["subcategories"][cat] = subcats
#         print(f"   └─ Found {len(subcats)} subcategories")

#         for sub in subcats[:2]:
#             print(f"      └─ Crawling subcategory: {sub}")
#             prods = get_products(sub)
#             output["products"][sub] = prods
#             print(f"         └─ Found {len(prods)} products")

#     # Save to JSON
#     with open("cvs_output.json", "w", encoding="utf-8") as f:
#         json.dump(output, f, indent=2, ensure_ascii=False)

#     print("[INFO]  Finished! Data saved to cvs_output.json")






import json
import time
import random
from curl_cffi import requests
from lxml import html
from urllib.parse import urljoin, urlparse, urlunparse

BASE_URL = "https://www.cvs.com/shop"

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

# ---------------- Deduplication Helper ---------------- #
def normalize_url(url: str) -> str:
    """Remove query strings, fragments, and trailing slashes for deduplication"""
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip('/'), '', '', ''))

def dedup_urls(base: str, hrefs: list[str]) -> list[str]:
    """Join, normalize, and deduplicate URLs"""
    normalized = [normalize_url(urljoin(base, href)) for href in hrefs]
    return sorted(set(normalized))

# ---------------- Request Helper ---------------- #
def get_page(url, retries=3):
    """Fetch page HTML with proxy, error handling, and retries."""
    session = requests.Session(impersonate="chrome120")
    session.headers.update({
        "user-agent": random.choice(USER_AGENTS),
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    })
    session.cookies.set("cvs_locale", "en_US")

    for attempt in range(retries):
        try:
            resp = session.get(url, proxies=PROXIES, timeout=45, verify=False)
            resp.raise_for_status()
            return resp.text
        except requests.RequestsError as e:
            if attempt < retries - 1:
                wait_time = 2 ** attempt * 5 + random.uniform(1, 3)
                print(f"[RETRY] Attempt {attempt + 1}/{retries} for {url}. Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                print(f"[ERROR] Failed to fetch {url} after {retries} attempts -> {e}")
    return None

# ---------------- Scraper Functions ---------------- #
def get_categories():
    """Fetch main categories from the CVS shop page."""
    page = get_page(BASE_URL)
    if not page:
        return []

    tree = html.fromstring(page)
    nodes = tree.xpath('//nav[@id="linkGroupShopalldepartments"]//a[@class="contentful link-group-anchor"]/@href')

    return dedup_urls(BASE_URL, nodes)

def get_subcategories(cat_url):
    """Extract subcategory URLs from a category."""
    page = get_page(cat_url)
    if not page:
        return []

    tree = html.fromstring(page)

    # Grab ANY shop link under this category page
    nodes = tree.xpath('//a[contains(@class, "pulse-text-black pulse-link viz-nav-cta-text")]/@href')

    return dedup_urls(cat_url, nodes)


def get_products(subcat_url):
    """Extract product URLs from a subcategory."""
    page = get_page(subcat_url)
    if not page:
        return []

    tree = html.fromstring(page)

    # Try direct product links in HTML
    nodes = tree.xpath('//a[contains(@class, "css-1dbjc4n r-1o9r03r r-1loqt21 r-qtbb1w r-u8s1d r-1wipuzn r-1sofzug r-1otgn73 r-1i6wzkk r-lrvibr")]/@href')

    if not nodes:
        print(f"[WARN] No <a> product links found in {subcat_url}. Products may load via API/JS.")

    return dedup_urls(subcat_url, nodes)

# ---------------- Main ---------------- #
if __name__ == "__main__":
    output = {"categories": [], "subcategories": {}, "products": {}}

    print("[INFO] Fetching categories...")
    categories = get_categories()
    output["categories"] = categories
    print(f"[INFO] Found {len(categories)} unique categories")

    for cat in categories[:3]:  # Limit to 3 for testing
        print(f"\n[INFO] Crawling category: {cat}")
        subcats = get_subcategories(cat)
        output["subcategories"][cat] = subcats
        print(f"   └─ Found {len(subcats)} unique subcategories")
        time.sleep(random.uniform(2, 5))

        for sub in subcats:  # Limit to 2 for testing
            print(f"      └─ Crawling subcategory: {sub}")
            prods = get_products(sub)
            output["products"][sub] = prods
            print(f"         └─ Found {len(prods)} unique products")
            time.sleep(random.uniform(1, 3))

    with open("cvs_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n[INFO] Finished! Data saved to cvs_output.json")
