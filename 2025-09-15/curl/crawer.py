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
#     try:
#         resp = session.get(url, proxies=PROXIES, timeout=30, verify=False)
#         resp.raise_for_status()
#         return resp.text
#     except Exception as e:
#         return None

# def get_categories():
#     page = get_page(BASE_URL)
#     if not page:
#         return []
#     tree = html.fromstring(page)
#     categories = tree.xpath('//a[@class="contentful link-group-anchor"]/@href')
#     return [href if href.startswith("http") else BASE_URL.rstrip("/") + href for href in categories]

# def get_subcategories(cat_url):
#     page = get_page(cat_url)
#     if not page:
#         return []
#     tree = html.fromstring(page)
#     subcats = tree.xpath('//a[contains(@href,"/shop/")]/@href')
#     return [href if href.startswith("http") else BASE_URL.rstrip("/") + href for href in subcats]

# def get_products(subcat_url):
#     page = get_page(subcat_url)
#     if not page:
#         return []
#     tree = html.fromstring(page)
#     products = tree.xpath('//a[contains(@href,"/product/")]/@href')
#     return [href if href.startswith("http") else BASE_URL.rstrip("/") + href for href in products]

# if __name__ == "__main__":
#     output = {"categories": [], "subcategories": {}, "products": {}}

#     # Step 1: Categories
#     categories = get_categories()
#     output["categories"] = categories

#     # Step 2: Subcategories for each category
#     for cat in categories:
#         subcats = get_subcategories(cat)
#         output["subcategories"][cat] = subcats

#         # Step 3: Products for each subcategory
#         for sub in subcats:
#             prods = get_products(sub)
#             output["products"][sub] = prods

#     # Save to JSON
#     with open("cvs_output.json", "w", encoding="utf-8") as f:
#         json.dump(output, f, indent=2, ensure_ascii=False)






import json
from curl_cffi import requests
from lxml import html

BASE_URL = "https://www.cvs.com/shop"

PROXIES = {
    "http": "http://scraperapi.country_code=us:504eeef7c076dfcf401adae86875886d@proxy-server.scraperapi.com:8001",
    "https": "http://scraperapi.country_code=us:504eeef7c076dfcf401adae86875886d@proxy-server.scraperapi.com:8001"
}

# Chrome 120 impersonation
session = requests.Session(impersonate="chrome120")

# Headers
session.headers.update({
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
})

# Example cookies
session.cookies.set("cvs_locale", "en_US")
session.cookies.set("aka_debug", "1")


def get_page(url):
    """Fetch page HTML with proxy and error handling."""
    try:
        resp = session.get(url, proxies=PROXIES, timeout=30, verify=False)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url} -> {e}")
        return None


def get_categories():
    """Extract category URLs."""
    page = get_page(BASE_URL)
    if not page:
        return []
    tree = html.fromstring(page)
    categories = tree.xpath('//a[@class="contentful link-group-anchor"]/@href')
    return [href if href.startswith("http") else BASE_URL.rstrip("/") + href for href in categories]


def get_subcategories(cat_url):
    """Extract subcategory URLs from a category."""
    page = get_page(cat_url)
    if not page:
        return []
    tree = html.fromstring(page)
    subcats = tree.xpath('//a[contains(@href,"/shop/")]/@href')
    return [href if href.startswith("http") else BASE_URL.rstrip("/") + href for href in subcats]


def get_products(subcat_url):
    """Extract product URLs from a subcategory."""
    page = get_page(subcat_url)
    if not page:
        return []
    tree = html.fromstring(page)
    # products = tree.xpath('//a[contains(@href,"/product/")]/@href')
    products = tree.xpath('//a[@class="css-1dbjc4n r-1p0dtai r-1loqt21 r-1d2f490 r-u8s1d r-zchlnj r-ipm5af r-1otgn73 r-1i6wzkk r-lrvibr"]/@href')

    return [href if href.startswith("http") else BASE_URL.rstrip("/") + href for href in products]


if __name__ == "__main__":
    output = {"categories": [], "subcategories": {}, "products": {}}

    print("[INFO] Fetching categories...")
    categories = get_categories()
    output["categories"] = categories
    print(f"[INFO] Found {len(categories)} categories")

    # Limit for testing (change/remove later)
    for cat in categories[:3]:
        print(f"[INFO] Crawling category: {cat}")
        subcats = get_subcategories(cat)
        output["subcategories"][cat] = subcats
        print(f"   └─ Found {len(subcats)} subcategories")

        for sub in subcats[:2]:
            print(f"      └─ Crawling subcategory: {sub}")
            prods = get_products(sub)
            output["products"][sub] = prods
            print(f"         └─ Found {len(prods)} products")

    # Save to JSON
    with open("cvs_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("[INFO]  Finished! Data saved to cvs_output.json")
