import logging
import time
import requests
from parsel import Selector
from pymongo import MongoClient
from urllib.parse import urljoin

from settings import (
    BASE_URL,
    HEADERS_PAGE as headers,
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_CATEGORY,
    REQUEST_DELAY,
)

class Crawler:
    """Kulud Category → Subcategory → Product URLs nested"""

    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.category_col = self.db[MONGO_COLLECTION_CATEGORY]

    def start(self):
        logging.info("Starting Kulud crawler...")

        # Step 1: Get main categories
        html = self.get_html(BASE_URL)
        if not html:
            logging.error("Failed to load main page")
            return

        sel = Selector(text=html)
        category_links = sel.xpath('//li[@class="has-babymenu"]/a/@href').getall()

        for cat_link in category_links:
            category_url = urljoin("https://kuludonline.com", cat_link)
            logging.info(f"Category: {category_url}")

            # Step 2: Get subcategories
            subcategories_urls = self.get_subcategories(category_url)
            subcategories_list = []

            # Step 3: Get products for each subcategory
            for sub_url in subcategories_urls:
                products = self.get_products(sub_url)
                subcategories_list.append({
                    "subcategory_url": sub_url,
                    "products": products
                })

            # Step 4: Save category with nested subcategories and products
            category_doc = {
                "category_url": category_url,
                "subcategories": subcategories_list
            }
            self.category_col.insert_one(category_doc)
            logging.info(f"Saved category: {category_url} with {len(subcategories_list)} subcategories")

            time.sleep(REQUEST_DELAY)

    def get_html(self, url):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        logging.warning(f"Failed to fetch: {url}")
        return None

    def get_subcategories(self, category_url):
        html = self.get_html(category_url)
        if not html:
            return []

        sel = Selector(text=html)
        divs = sel.xpath('//div[contains(@class,"card js-collection-item")]')
        sub_urls = []
        for div in divs:
            href = div.xpath('.//a[@class="card__whole-link"]/@href').get()
            if href:
                full_url = urljoin("https://kuludonline.com", href)
                sub_urls.append(full_url)

        if not sub_urls:
            sub_urls = [category_url]  # fallback

        logging.info(f"Found {len(sub_urls)} subcategories in {category_url}")
        return sub_urls

    def get_products(self, subcat_url):
        """Return a list of product URLs for a subcategory"""
        products = []
        page_url = subcat_url

        while page_url:
            html = self.get_html(page_url)
            if not html:
                break

            sel = Selector(text=html)
            divs = sel.xpath('//div[contains(@class,"product-item card")]')
            for div in divs:
                href = div.xpath('.//a[contains(@class,"product-item__image")]/@href').get()
                if href:
                    product_url = urljoin("https://kuludonline.com", href)
                    products.append(product_url)

            # Check next page
            next_page = sel.xpath('//a[@class="pagination__next"]/@href').get()
            page_url = urljoin("https://kuludonline.com", next_page) if next_page else None
            time.sleep(REQUEST_DELAY)

        logging.info(f"Found {len(products)} products in {subcat_url}")
        return products

    def close(self):
        self.client.close()
        logging.info("MongoDB connection closed.")


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()




