
import os
import time
import json
import requests
from urllib.parse import urljoin
from parsel import Selector
from pymongo import MongoClient  

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


session = requests()

##############################
# CRAWLER: DEPARTMENTS → CATEGORIES → SUBCATEGORIES
##############################

BASE_URL = "https://www.homedepot.ca/en/home/all-departments.html"
html = session.get(BASE_URL, headers=HEADERS, timeout=20).text
sel = Selector(text=html)

results = []

for dept in sel.xpath('//section[@class="hdca-cms-sitemap"]/ul/li'):
    dept_name = dept.xpath('normalize-space(.//h2//a/text())').get()
    dept_url = dept.xpath('.//h2//a/@href').get()

    for cat in dept.xpath('./ol/li[contains(@class,"hdca-cms-sitemap__linklist-item")]'):
        cat_name = cat.xpath('normalize-space(.//a[contains(@class,"hdca-button2")])').get()
        cat_url = cat.xpath('.//a[contains(@class,"hdca-button2")]/@href').get()
        subcats = cat.xpath('./ol/li/a')

        if subcats:
            for sub in subcats:
                results.append({
                    "department": dept_name,
                    "department_url": dept_url,
                    "category": cat_name,
                    "category_url": cat_url,
                    "subcategory": sub.xpath('normalize-space(text())').get(),
                    "subcategory_url": sub.xpath('@href').get()
                })
        else:
            results.append({
                "department": dept_name,
                "department_url": dept_url,
                "category": cat_name,
                "category_url": cat_url,
                "subcategory": None,
                "subcategory_url": None
            })

##############################
# PARSER: JSON-LD / hdca-(site shortname hdca)state extraction
##############################

def extract_products_from_hdca_state(html):#collect html from home depot hdca
    sel = Selector(text=html)
    urls = []

    script_json = sel.xpath("//script[@id='hdca-state']/text()").get()
    if script_json:
        data = json.loads(script_json)
        for pid, info in data.items():
            urls.append(pid)  # can also append product URL if available
    return urls

def parse_product_page(url):
    """Extract product details from a product page"""
    r = session.get(url, headers=HEADERS, timeout=20)
    sel = Selector(text=r.text)

    # Example: hdca-state
    script_json = sel.xpath("//script[@id='hdca-state']/text()").get()
    if not script_json:
        return None

    data = json.loads(script_json)
    product_id = list(data.keys())[0]
    product = data[product_id]["b"]

    details = {
        "name": product.get("name"),
        "manufacturer": product.get("manufacturer"),
        "sku": product.get("code"),
        "model_number": product.get("modelNumber"),
        "price": product.get("price", {}).get("formattedValue"),
        "currency": product.get("price", {}).get("currencyIso"),
        "description": product.get("description"),
        "categories": [c.get("name") for c in product.get("categories", [])],
        "images": [i.get("url") for i in product.get("images", [])],
        "alternate_images": [i.get("url") for i in product.get("alternateImages", [])],
        "dimensions": {
            "width": product.get("itemWidth"),
            "height": product.get("itemHeight"),
            "depth": product.get("itemDepth"),
        },
        "weight": product.get("itemWeight"),
        "reviews_count": product.get("numberOfReviews"),
        "average_rating": product.get("averageRating")
    }

    return details

##############################
# FEASIBILITY FINDINGS
##############################

"""

1. Some pages may require VPN for certain US-only variants.
2. Reviews may require API key or special headers; monitor rate limits.

"""
