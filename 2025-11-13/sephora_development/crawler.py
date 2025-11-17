import requests
import logging
import time
import urllib.parse
from parsel import Selector
from settings import (
    BASE_URL, HEADERS, client, collection_categories,
    MAIN_CATEGORY_BLOCKS_XPATH, MAIN_CATEGORY_NAME_XPATH,
    SUB_CATEGORY_LINKS_XPATH, POLITE_DELAY,
    PRODUCT_URL_XPATH, NEXT_PAGE_XPATH
)

class Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def start(self):
        """Start crawling homepage and categories"""
        response = self.session.get(BASE_URL)
        if response.status_code != 200:
            logging.error(f"Failed to load homepage: {response.status_code}")
            return

        home_sel = Selector(response.text)
        main_categories = home_sel.xpath(MAIN_CATEGORY_BLOCKS_XPATH)
        logging.info(f"Found {len(main_categories)} main categories.")

        for main_element in main_categories:
            main_name = main_element.xpath(MAIN_CATEGORY_NAME_XPATH).get(default='').strip()
            if not main_name:
                continue

            sub_links = main_element.xpath(SUB_CATEGORY_LINKS_XPATH)

            for sub in sub_links:
                sub_name = sub.xpath('text()').get(default='').strip()
                sub_href = sub.xpath('@href').get()
                if not sub_href or sub_href.count('/') < 3:
                    continue

                full_sub_url = urllib.parse.urljoin(BASE_URL, sub_href)
                logging.info(f"  [Sub-Category] {sub_name} -> {full_sub_url}")

                # Crawl products in this sub-category
                product_urls = self.parse_item(full_sub_url)

                # Save into MONGO_COLLECTION_CATEGORY
                doc = {
                    "category_url": full_sub_url,
                    "main_category": main_name,
                    "sub_category": sub_name,
                    "products": product_urls
                }
                try:
                    collection_categories.insert_one(doc)
                    logging.info(f"Saved '{main_name} > {sub_name}' with {len(product_urls)} products")
                except Exception as e:
                    logging.warning(f"MongoDB insert failed: {e}")

    def parse_item(self, category_url):
        """Crawl all products from a category with pagination"""
        collected = set()
        next_page = category_url

        while next_page:
            logging.info(f"    Scraping page: {next_page}")
            time.sleep(POLITE_DELAY)
            resp = self.session.get(next_page)
            if resp.status_code != 200:
                logging.warning(f"Failed to fetch page: {resp.status_code}")
                break

            sel = Selector(resp.text)
            product_paths = sel.xpath(PRODUCT_URL_XPATH).getall()
            for path in product_paths:
                collected.add(urllib.parse.urljoin(BASE_URL, path))

            next_link = sel.xpath(NEXT_PAGE_XPATH).get()
            next_page = urllib.parse.urljoin(BASE_URL, next_link) if next_link else None

        return list(collected)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    crawler = Crawler()
    crawler.start()
    client.close()

