import requests
import time
import logging
from urllib.parse import urljoin
from lxml import html

# ---------------------- CONFIGURATION ----------------------
CATEGORY_URLS = [
    "https://shop.billa.at/kategorie/gemuese-13757",
    "https://shop.billa.at/kategorie/brot-und-gebaeck-13770",
    "https://shop.billa.at/kategorie/suesses-und-salziges-14057",
]


OUTPUT_FILE = "product_urls.txt"
MAX_PRODUCTS_PER_CATEGORY = 1000
PAGE_LIMIT = 100
REQUEST_DELAY = 2  # seconds between requests

# Pagination type: "page", "offset", "cursor", "api", or "tag"
PAGINATION_TYPE = "page"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ---------------------- LOGGER SETUP ----------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ---------------------- CORE EXTRACTION ----------------------
def extract_product_urls_using_xpath(page_content, base_url):
    """
    Extract product URLs using XPath from HTML.
    Adjust the XPath according to your site's structure.
    """
    tree = html.fromstring(page_content)
    hrefs = tree.xpath("//a[contains(@class, 'ws-product-tile__link')]/@href")
    product_urls = [urljoin(base_url, href) for href in hrefs if href.strip()]
    return list(set(product_urls))  # Deduplicate


# ---------------------- PAGINATION METHODS ----------------------
def paginate_by_page(category_url, page):
    """URL pattern: ?page=1&limit=100"""
    return f"{category_url}?page={page}&limit={PAGE_LIMIT}"

def paginate_by_offset(category_url, page):
    """URL pattern: ?offset=0&limit=100"""
    offset = (page - 1) * PAGE_LIMIT
    return f"{category_url}?offset={offset}&limit={PAGE_LIMIT}"

def paginate_by_cursor(category_url, cursor_token):
    """Simulated cursor-based pagination"""
    return f"{category_url}?cursor={cursor_token}"

def paginate_by_api(api_url, page):
    """Example API pagination"""
    return f"{api_url}?page={page}&limit={PAGE_LIMIT}"

def paginate_by_tag(page_content, base_url):
    """
    Extract next-page link from HTML using XPath.
    Looks for <a> tags with 'next' or numeric pagination links.
    """
    tree = html.fromstring(page_content)
    
    # Example: find link text like 'Next' or rel='next'
    next_links = tree.xpath(
        "//a[contains(translate(text(),'NEXT','next'),'next') or contains(@rel,'next')]/@href"
    )
    
    # If not found, try numbered pagination (like <a>2</a>)
    if not next_links:
        next_links = tree.xpath("//a[contains(@class,'pagination') or re:test(text(),'^[0-9]+$')]/@href",
                                namespaces={'re': 'http://exslt.org/regular-expressions'})
        
    
    if next_links:
        next_url = urljoin(base_url, next_links[0])
        return next_url
    return None


# ---------------------- MAIN PAGINATION CONTROLLER ----------------------
def get_paginated_products(category_url, pagination_type="page"):
    all_product_urls = []
    page = 1
    cursor_token = None
    next_page_url = category_url

    while len(all_product_urls) < MAX_PRODUCTS_PER_CATEGORY and next_page_url:
        logging.info(f"Fetching: {next_page_url}")

        try:
            response = requests.get(next_page_url, headers=HEADERS, timeout=20)
            if response.status_code != 200:
                logging.warning(f"Non-200 status {response.status_code} for {next_page_url}")
                break

            # Try JSON parsing first (for APIs)
            new_urls = []
            try:
                data = response.json()
                if "next_cursor" in data:
                    cursor_token = data["next_cursor"]
                if "products" in data:
                    for p in data["products"]:
                        if "url" in p:
                            new_urls.append(urljoin(category_url, p["url"]))
            except ValueError:
                # HTML parsing fallback
                new_urls = extract_product_urls_using_xpath(response.text, category_url)

            # Stop if no new URLs
            if not new_urls:
                logging.info("No more products found, stopping pagination.")
                break

            for url in new_urls:
                if url not in all_product_urls:
                    all_product_urls.append(url)
                    if len(all_product_urls) >= MAX_PRODUCTS_PER_CATEGORY:
                        break
                    if page > 50:
                        logging.info("Reached page limit, stopping.")
                        break


            logging.info(f"Collected: {len(all_product_urls)} products so far.")

            # ----------- PAGINATION SWITCH -----------
            if pagination_type == "page":
                next_page_url = paginate_by_page(category_url, page + 1)
            elif pagination_type == "offset":
                next_page_url = paginate_by_offset(category_url, page + 1)
            elif pagination_type == "cursor" and cursor_token:
                next_page_url = paginate_by_cursor(category_url, cursor_token)
            elif pagination_type == "api":
                next_page_url = paginate_by_api(category_url, page + 1)
            elif pagination_type == "tag":
                next_page_url = paginate_by_tag(response.text, category_url)
            else:
                next_page_url = None

            page += 1
            time.sleep(REQUEST_DELAY)

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            break

    return all_product_urls


# ---------------------- SAVE FUNCTION ----------------------
def save_to_txt(filename, urls):
    with open(filename, "a", encoding="utf-8") as f:
        for url in urls:
            f.write(url + "\n")


# ---------------------- MAIN EXECUTION ----------------------
if __name__ == "__main__":
    open(OUTPUT_FILE, "w").close()  # clear old file
    grand_total = 0

    for category in CATEGORY_URLS:
        logging.info(f"Starting scrape for category: {category}")
        product_urls = get_paginated_products(category, PAGINATION_TYPE)
        save_to_txt(OUTPUT_FILE, product_urls)
        logging.info(f" Saved {len(product_urls)} URLs from {category}")
        grand_total += len(product_urls)

    logging.info(f" GRAND TOTAL PRODUCTS SAVED: {grand_total}")
    logging.info(f" All URLs saved to: {OUTPUT_FILE}")





