
import requests
from parsel import Selector
from urllib.parse import urljoin, urlparse
import json
import time


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

##############################CRAWLER##############################
BASE_URL = "https://www.sephora.sg"
response = requests.get(BASE_URL, headers=headers)
home_tree = Selector(text=response.text)

MAIN_CATEGORY_BLOCKS_XPATH = '//div[contains(@class, "menu-dropdown")][.//div[contains(@class, "categories-dropdown-container")]]'
MAIN_CATEGORY_NAME_XPATH = './/div[contains(@class, "dropdown-trigger")]//div[contains(@class, "text-container")]/text()'
SUB_CATEGORY_LINKS_XPATH = './/div[contains(@class, "categories-dropdown-container")]//a[starts-with(@href, "/categories/")]'
PRODUCT_URL_XPATH = '//a[contains(@class, "product-card-description")]/@href'
NEXT_PAGE_XPATH = '//a[contains(@class, "pagination-item") and contains(@class, "next-page")]/@href'

for main_element in home_tree.xpath(MAIN_CATEGORY_BLOCKS_XPATH):
    main_cat_name = main_element.xpath(MAIN_CATEGORY_NAME_XPATH).get()
    if main_cat_name:
        for link in main_element.xpath(SUB_CATEGORY_LINKS_XPATH):
            sub_name = link.xpath("text()").get().strip()
            sub_href = link.attrib.get('href')
            if sub_href and sub_href.count('/') >= 3:
                sub_url = urljoin(BASE_URL, sub_href)

                # PAGINATION LOGIC
                current_page = sub_url
                while current_page:
                    print(f"    -> Scraping page: {current_page}")
                    resp = requests.get(current_page, headers=headers)
                    tree = Selector(text=resp.text)
                    product_paths = tree.xpath(PRODUCT_URL_XPATH).getall()
                    for path in product_paths:
                        product_url = urljoin(BASE_URL, path)
                    next_button = tree.xpath(NEXT_PAGE_XPATH).get()
                    current_page = urljoin(BASE_URL, next_button) if next_button else None
                    time.sleep(1)

##############################PARSER##############################
API_BASE = "https://www.sephora.sg/api/v2.6/products/"
INCLUDE_PARAMS = "variants.filter_values,variants.ingredient_preference,featured_ad.virtual_bundle.bundle_elements,product_articles,filter_types"

parsed = urlparse("sephoria_urls_test.json")
parts = parsed.path.strip("/").split("/")
product_slug = parts[1]
variant_slug = parts[3] if len(parts) > 3 else None
api_url = f"{API_BASE}{product_slug}?include={INCLUDE_PARAMS}" if not variant_slug else f"{API_BASE}{product_slug}?v={variant_slug}&include={INCLUDE_PARAMS}"
resp = requests.get(api_url, headers=headers)
data = resp.json().get("data", {}).get("attributes", {})
product = {
        "retailer_name": "Sephora SG",
        "product_name": attributes.get("name"),
        "brand": attributes.get("brand", {}).get("name") if attributes.get("brand") else None,
        "grammage_quantity": attributes.get("size_value"),
        "grammage_unit": attributes.get("size_unit"),
        "original_price": original_price,
        "selling_price": selling_price,
        "promotion_description": promo_label,
        "pdp_url": f"https://www.sephora.sg{path}",
        "image_url": (attributes.get("image_urls") or [None])[0],
        "ingredients": clean_html(attributes.get("ingredients")),
        "disclaimer": clean_html(attributes.get("safety_warning")),
        "product_description": clean_html(attributes.get("description")),
        "product_texture": attributes.get("texture"),
        "skin_type": attributes.get("skin_type"),
        "colour": attributes.get("colour"),
        "hair_type": attributes.get("hair_type"),
        "skin_tone": attributes.get("skin_tone"),
    }

##############################FINDINGS##############################
# Pagination works for subcategories
# Product URLs follow /products/<slug> format
# API returns structured JSON, variant handling avoids 422
# Some reviews/size/color fields may require region-specific access 
