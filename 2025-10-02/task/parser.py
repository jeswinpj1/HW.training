#!/usr/bin/env python3
import time
import re
from pymongo import MongoClient
from playwright.sync_api import sync_playwright

class ProductParser:
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="styleunion"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.categories_col = self.db["categories"]
        self.products_col = self.db["products"]
        self.product_limit = 300

    def start_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def close_browser(self):
        try:
            self.context.close()
            self.browser.close()
        finally:
            self.playwright.stop()

    def get_product_urls(self):
        urls = []
        cursor = self.categories_col.find({}, {"category_url": 1, "subcategories": 1})
        for cat in cursor:
            category_url = cat.get("category_url")
            for sub in cat.get("subcategories", []):
                sub_url = sub.get("subcategory_url")
                for prod_url in sub.get("products", []):
                    if prod_url:
                        urls.append({
                            "category_url": category_url,
                            "subcategory_url": sub_url,
                            "product_url": prod_url
                        })
        return urls[:self.product_limit]

    def _looks_like_specs(self, text):
        if not text:
            return False
        lower = text.lower()
        if ':' in text:
            return True
        for kw in ['fabric', 'weave', 'wash', 'fit', 'material', 'composition', 'gsm', 'care']:
            if kw in lower:
                return True
        if len(text) < 120 and re.search(r'\(\d+%|\d+%|\)', text):
            return True
        return False

    def _parse_specs(self, text):
        specs = {}
        if not text:
            return specs
        text2 = re.sub(r'•|\u2022|\t', '\n', text)
        parts = [p.strip() for p in re.split(r'\r?\n|;|\|', text2) if p.strip()]
        for part in parts:
            if ':' in part:
                k, v = part.split(':', 1)
                specs[k.strip()] = v.strip()
            elif '-' in part and len(part.split('-', 1)) == 2:
                k, v = part.split('-', 1)
                specs[k.strip()] = v.strip()
            else:
                m = re.match(r'^(?P<k>[A-Za-z ]{3,30})[:\s\-]+(?P<v>.+)$', part)
                if m:
                    specs[m.group('k').strip()] = m.group('v').strip()
                else:
                    specs.setdefault('notes', []).append(part)
        return specs

    def scrape_product_details(self, product_url, retries=2):
        for attempt in range(1, retries + 1):
            try:
                self.page.goto(product_url, timeout=30000, wait_until="domcontentloaded")
                # --- basic fields ---
                title_elem = self.page.query_selector('//h1[contains(@class,"product-title")]')
                title = title_elem.text_content().strip() if title_elem else None

                price_elem = self.page.query_selector('//span[contains(@class,"price-item--regular")]')
                price = price_elem.text_content().strip() if price_elem else None

                color_elem = self.page.query_selector('//p[contains(translate(.,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),"color")]/span')
                if not color_elem:
                    color_elem = self.page.query_selector('//label[contains(translate(.,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),"color")]/span')
                color = color_elem.text_content().strip() if color_elem else None

                size_elems = self.page.query_selector_all('//p[contains(translate(.,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),"size")]/span')
                sizes = [e.text_content().strip() for e in size_elems] if size_elems else None

                sku_elem = self.page.query_selector('//span[@id="variantSku"]')
                sku = sku_elem.text_content().strip() if sku_elem else None

                # --- Description & Product Details ---
                panels = self.page.query_selector_all('//div[contains(@class,"acc__panel")]')
                desc_text = None
                detail_text = None

                for panel in panels:
                    try:
                        header = panel.evaluate(
                            "el => (el.previousElementSibling && el.previousElementSibling.innerText) ? el.previousElementSibling.innerText.trim().toLowerCase() : ''"
                        )
                    except Exception:
                        header = ""

                    content = panel.text_content().strip()
                    if not content:
                        continue

                    if header:
                        if any(k in header for k in ['description', 'about', 'overview', 'product description', 'product info', 'details']):
                            if not desc_text or len(content) > len(desc_text):
                                desc_text = content
                            continue
                        if any(k in header for k in ['product', 'detail', 'spec', 'fabric', 'weave', 'wash', 'fit', 'specification']):
                            if not detail_text or len(content) > len(detail_text):
                                detail_text = content
                            continue

                    if self._looks_like_specs(content):
                        if not detail_text:
                            detail_text = content
                    else:
                        if not desc_text or len(content) > len(desc_text):
                            desc_text = content
                        elif not detail_text:
                            detail_text = content

                if desc_text and self._looks_like_specs(desc_text) and not detail_text:
                    detail_text = desc_text
                    desc_text = None

                product_detail_parsed = self._parse_specs(detail_text) if detail_text else {}

                return {
                    "product_url": product_url,
                    "title": title,
                    "price": price,
                    "color": color,
                    "sku": sku,
                    "sizes": sizes,
                    "description": desc_text or None,
                    "wash_and_care": detail_text or None,
                }

            except Exception as e:
                print(f"Timeout or scrape error (attempt {attempt}/{retries}): {product_url} -> {e}")
                time.sleep(2)
                continue

        print(f"Skipping product after {retries} attempts: {product_url}")
        return None

    def save_product_details(self, details, category_url, subcategory_url):
        if not details:
            return  # skip saving if details is None
        details["category_url"] = category_url
        details["subcategory_url"] = subcategory_url
        self.products_col.update_one(
            {"product_url": details["product_url"]},
            {"$set": details},
            upsert=True
        )

    def run(self):
        self.start_browser()
        total_count = 0
        try:
            product_urls = self.get_product_urls()
            for product in product_urls:
                details = self.scrape_product_details(product["product_url"])
                if not details:
                    continue
                self.save_product_details(details, product["category_url"], product["subcategory_url"])
                total_count += 1
                print(f"Scraped {total_count}/{len(product_urls)}: {product['product_url']}")
        finally:
            self.close_browser()
            print(f"Total products scraped: {total_count}")


if __name__ == "__main__":
    parser = ProductParser()
    parser.run()
