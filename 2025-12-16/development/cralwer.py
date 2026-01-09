import logging
import json
import requests
from parsel import Selector
from urllib.parse import urljoin
from pymongo import MongoClient
from settings import HEADERS, MONGO_COLLECTION_PRODUCT, MONGO_DB

logging.basicConfig(level=logging.INFO)


class Crawler:
    """HomeDepot Category & Product URL Crawler"""

    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION_PRODUCT]
        self.visited = set()

    def start(self):
        """Start crawling"""

        # ---------- STEP 1: FETCH CATEGORY PAGE ----------
        start_url = "https://www.homedepot.ca/en/home/all-departments.html"
        logging.info(f"Fetching category page: {start_url}")

        max_retries = 3
        response = None

        for attempt in range(1, max_retries + 1):
            try:
                logging.info(f"Attempt {attempt}: Fetching category page")
                response = requests.get(start_url, headers=HEADERS, timeout=30)
                break
            except requests.exceptions.ReadTimeout:
                logging.warning("Category page timeout, retrying...")
            except requests.exceptions.RequestException as e:
                logging.error(f"Category page request failed: {e}")
                return

        if not response or response.status_code != 200:
            logging.error("Failed to fetch category page after retries")
            return

        category_urls = self.parse_item(response, {"mode": "category"})

        # ---------- STEP 2: CRAWL PRODUCT PAGES ----------
        for category_url in category_urls:
            if not category_url:
                continue

            page_queue = {category_url}

            while page_queue:
                url = page_queue.pop()

                if url in self.visited:
                    continue
                self.visited.add(url)

                logging.info(f"Fetching: {url}")

                try:
                    response = requests.get(url, headers=HEADERS, timeout=30)
                except requests.exceptions.ReadTimeout:
                    logging.warning(f"Read timeout, skipping: {url}")
                    continue
                except requests.exceptions.RequestException as e:
                    logging.warning(f"Request error {url}: {e}")
                    continue

                if response.status_code != 200:
                    logging.warning(f"Non-200 status {response.status_code} for {url}")
                    continue

                next_pages = self.parse_item(
                    response,
                    {"mode": "product", "base_url": url}
                )

                for next_page in next_pages:
                    if next_page not in self.visited:
                        page_queue.add(next_page)

    def parse_item(self, response, meta):
        """Parse items"""

        sel = Selector(text=response.text)

        # ---------- CATEGORY MODE ----------
        if meta.get("mode") == "category":
            category_urls = set()

            for dept in sel.xpath('//section[@class="hdca-cms-sitemap"]/ul/li'):
                for cat in dept.xpath(
                    './/ol/li[contains(@class,"hdca-cms-sitemap__linklist-item")]'
                ):
                    cat_url = cat.xpath(
                        './/a[contains(@class,"hdca-button2")]/@href'
                    ).get()
                    if cat_url:
                        category_urls.add(cat_url)

            logging.info(f"Total categories found: {len(category_urls)}")
            return category_urls

        # ---------- PRODUCT MODE ----------
        elif meta.get("mode") == "product":
            base_url = meta.get("base_url")
            pagination_links = set()

            for script in sel.xpath('//script[@type="application/ld+json"]/text()').getall():
                try:
                    data = json.loads(script)
                    offers = (
                        data.get("mainEntity", {})
                        .get("offers", {})
                        .get("itemOffered", [])
                    )

                    if isinstance(offers, list):
                        for product in offers:
                            product_url = product.get("url")
                            if product_url:
                                item = {
                                    "product_url": product_url,
                                    "category_url": base_url
                                }
                                logging.info(item)
                                try:
                                    self.collection.insert_one(item)
                                except Exception:
                                    pass
                except Exception:
                    continue

            links = sel.xpath(
                '//a[contains(@class,"acl-pagination__item--link")]/@href'
            ).getall()

            for link in links:
                pagination_links.add(urljoin(base_url, link))

            return pagination_links

        return set()

    def close(self):
        """Close Mongo connection"""
        self.client.close()


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
