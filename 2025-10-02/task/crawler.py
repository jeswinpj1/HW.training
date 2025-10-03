#!/usr/bin/env python3
import time
from pymongo import MongoClient
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from lxml import html

class StyleUnionScraper:
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="styleunion"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.categories_col = self.db["categories"]

    def start_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def close_browser(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def scrape_categories(self, url="https://styleunion.in"):
        self.page.goto(url, timeout=60000)
        time.sleep(3)

        content = self.page.content()
        tree = html.fromstring(content)
        category_elements = tree.xpath('//ul[@aria-label="Men"]/li')[1:5]

        categories = []
        for li in category_elements:
            category_url = li.xpath('.//a/@href')
            category_url = 'https://styleunion.in' + category_url[0] if category_url else None

            subcategories = li.xpath('.//ul/li/a/@href')
            subcategories = ['https://styleunion.in' + sub for sub in subcategories] if subcategories else [None]

            categories.append({
                "category_url": category_url,
                "subcategories": [{"subcategory_url": sub, "products": []} for sub in subcategories]
            })

            # Insert or update category
            self.categories_col.update_one(
                {"category_url": category_url},
                {"$set": {"subcategories": [{"subcategory_url": sub, "products": []} for sub in subcategories]}},
                upsert=True
            )

        return categories

    def scrape_products(self, category_url, subcategory_url):
        self.page.goto(subcategory_url, timeout=60000)
        time.sleep(3)
        products = set()
        last_height = None

        while True:
            content = self.page.content()
            tree = html.fromstring(content)
            product_links = tree.xpath('//div[@class="prod-image image_portrait js-product-image"]/a/@href')
            for link in product_links:
                full_link = 'https://styleunion.in' + link if link else None
                products.add(full_link)

            current_height = self.page.evaluate("document.body.scrollHeight")
            if last_height == current_height:
                break
            last_height = current_height
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Save products inside the subcategory of the category document
        self.categories_col.update_one(
            {"category_url": category_url, "subcategories.subcategory_url": subcategory_url},
            {"$set": {"subcategories.$.products": list(products)}}
        )

        return list(products)

    def run(self):
        self.start_browser()
        try:
            categories = self.scrape_categories()
            for cat in categories:
                for sub in cat["subcategories"]:
                    sub_url = sub["subcategory_url"]
                    print(f"Scraping products from: {sub_url}")
                    self.scrape_products(cat["category_url"], sub_url)
        finally:
            self.close_browser()


if __name__ == "__main__":
    scraper = StyleUnionScraper()
    scraper.run()
