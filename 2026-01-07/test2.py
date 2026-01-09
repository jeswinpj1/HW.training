import requests
from parsel import Selector
import json
import time

BASE_URL = "https://www.mueller.at"
CATEGORY_FILE = "/home/user/HW.training/parfuemerie_categories.txt"
OUTPUT_FILE = "/home/user/HW.training/product_urls.json"

session = requests.Session()

# IMPORTANT HEADERS (ANTI-403)
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "identity",   # critical
    "Referer": BASE_URL,
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
})

# COOKIES (ONCE)
session.cookies.update({
    "__Secure-CDNCID": "a3QR1q1wiv7yKyG48yHYWe5NnBfuE+YqtwsVeqFriSXCzeLG19rNRpLWRtaMqAcT2EQHaKAq6TwoFfCJoilzZrGtwEJY9paR9e7dlag8YlrTQyFqGZWQrdNaP8HbWYE1",
    "INGRESSCOOKIE": "1767765756.872.1681.677435|2287d48963360908c030ff2bb9f3cc00",
})

# READ CATEGORY URLS
category_urls = []
with open(CATEGORY_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("URL:"):
            category_urls.append(line.replace("URL:", "").strip())

print(f"Found {len(category_urls)} category URLs")

product_urls = set()
visited_pages = set()

def scrape_page(url):
    print(f"Fetching: {url}")
    r = session.get(url, timeout=30)

    if r.status_code != 200:
        print(f"Blocked ({r.status_code}) → {url}")
        return []

    sel = Selector(r.text)

    # PRODUCT URLS
    links = sel.xpath(
        '//div[contains(@class,"product-tile_component_product-tile__content")]//a/@href'
    ).getall()

    for link in links:
        if link.startswith("/p/"):
            product_urls.add(BASE_URL + link)

    # PAGINATION
    next_pages = sel.xpath(
        '//a[contains(@class,"paginator_component_paginator__item-link")]/@href'
    ).getall()

    return [BASE_URL + p for p in next_pages if BASE_URL + p not in visited_pages]

# CRAWL ALL CATEGORIES
for category in category_urls:
    queue = [category]

    while queue:
        page = queue.pop(0)
        if page in visited_pages:
            continue

        visited_pages.add(page)
        new_pages = scrape_page(page)
        queue.extend(new_pages)

        time.sleep(1.2)  # anti-ban delay

# SAVE JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(sorted(product_urls), f, indent=2, ensure_ascii=False)

print(f"\n DONE: {len(product_urls)} product URLs saved")
