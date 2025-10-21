#!/usr/bin/env python3
"""
feasibility.py
Feasibility check for https://shop.billa.at
Goal: Validate extraction of category, subcategory, and product links + basic parser test.
"""

import requests
import random
from scrapy import Selector
from urllib.parse import urljoin

# --------------------------------------------------- PROXY + HEADERS --------------------------------------------------- #

PROXY_LIST = []  # Add proxies if needed
PROXY = random.choice(PROXY_LIST) if PROXY_LIST else None
proxies = {"http": f"http://{PROXY}", "https": f"http://{PROXY}"} if PROXY else None

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-GB,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"122\", \"Chromium\";v=\"122\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Linux\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# --------------------------------------------------- BASE URLS --------------------------------------------------- #
BASE_URL = "https://shop.billa.at"
CATEGORY_URLS = [
    "https://shop.billa.at/kategorie/gemuese-13757",
    "https://shop.billa.at/kategorie/brot-und-gebaeck-13770",
    "https://shop.billa.at/kategorie/suesses-und-salziges-14057",
]

# --------------------------------------------------- CRAWLER TESTS --------------------------------------------------- #

# --- Fetch subcategories ---
category_url = CATEGORY_URLS[0]
response = requests.get(category_url, headers=headers, proxies=proxies, timeout=30)
sel = Selector(text=response.text)

# Example: subcategory links under the main category
sub_links = sel.xpath("//a[contains(@class,'ws-category-tile__link')]/@href").extract()
sub_links = [urljoin(BASE_URL, link) for link in sub_links]
print(f"Found {len(sub_links)} subcategories:")
for link in sub_links[:5]:
    print("  ", link)

# --- Fetch product listing links from a category ---
listing_url = category_url
response = requests.get(listing_url, headers=headers, proxies=proxies, timeout=30)
sel = Selector(text=response.text)

product_links = sel.xpath("//a[contains(@class,'ws-product-tile__link')]/@href").extract()
product_links = [urljoin(BASE_URL, link) for link in product_links]
print(f"\nFound {len(product_links)} product links:")
for link in product_links[:5]:
    print("  ", link)

# --------------------------------------------------- PARSER TEST --------------------------------------------------- #

if product_links:
    sample_product = product_links[0]
    print(f"\nTesting product detail parsing for: {sample_product}")

    res = requests.get(sample_product, headers=headers, proxies=proxies, timeout=30)
    sel = Selector(text=res.text)

    # Extract fields
    name = sel.xpath("//h1/text()").extract_first()
    price = sel.xpath("//span[contains(@class,'price')]/text()").extract_first()
    description = sel.xpath("//div[contains(@class,'product-description')]//text()").extract()
    description = " ".join([d.strip() for d in description if d.strip()])

    print("\nProduct Name:", name)
    print("Price:", price)
    print("Description Snippet:", description[:200])

# --------------------------------------------------- FINDINGS --------------------------------------------------- #

"""
Findings:
- Product URLs can be extracted using class 'ws-product-tile__link'.
- Subcategories are accessible from category tiles (class 'ws-category-tile__link').
- Product detail pages contain name, price, and description in standard structure.
- Pagination appears via `?page=` pattern but may require scroll or JS handling for full lists.
- No API endpoints directly exposed for listing — browser automation might be required if lazy loading is used.
- Feasible to crawl using requests + lxml for static pages, otherwise fallback to Playwright for dynamic content.
"""

# --------------------------------------------------- WORKFLOW --------------------------------------------------- #
"""
Workflow Plan:
1. Start from CATEGORY_URLS list.
2. Extract all subcategories using XPath.
3. From each subcategory, extract product URLs using same pattern.
4. If pagination is found, increment ?page= or handle lazy load.
5. Parse each product page for name, price, and description.
6. Store URLs or product data to file or MongoDB.
"""

