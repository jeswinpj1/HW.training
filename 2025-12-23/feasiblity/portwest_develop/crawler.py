# import logging
# import time
# import requests
# from parsel import Selector
# from pymongo import MongoClient
# from urllib.parse import urlparse, urljoin
# from settings import headers, MONGO_DB, MONGO_COLLECTION_CATEGORY

# BASE = "https://www.portwest.com"

# class Crawler:
#     """Crawling URLs from Portwest"""

#     def __init__(self):
#         self.client = MongoClient("mongodb://localhost:27017/")
#         self.mongo = self.client[MONGO_DB]

#     def start(self):
#         """Request homepage and extract categories"""
#         response = requests.get(BASE, headers=headers, timeout=30)
#         if response.status_code != 200:
#             logging.error("Failed to fetch homepage")
#             return

#         sel = Selector(text=response.text)
#         category_urls = sel.xpath('//div[@class="menu-title"]/a/@href').getall()
#         category_urls = [urljoin(BASE, url) for url in category_urls]

#         for url in category_urls:
#             if "/products/" not in url:
#                 continue

#             logging.info(f"Processing category: {url}")
#             parts = urlparse(url).path.strip("/").split("/")
#             if len(parts) < 5:
#                 logging.warning(f"Invalid category format: {url}")
#                 continue

#             level, group, category_id, subcategory_id = parts[1], parts[2], parts[3], parts[4]
#             if not category_id.isdigit() or not subcategory_id.isdigit():
#                 logging.warning(f"Skipping non-numeric category: {url}")
#                 continue

#             meta = {
#                 "category": url,
#                 "offset": 0,
#                 "seen": set()
#             }

#             # 1️⃣ First page from category HTML
#             self.fetch_category_page(url, meta)

#             # 2️⃣ Paginate with AJAX endpoint
#             offset = 0
#             while True:
#                 api_url = f"{BASE}/products/load_more_category_products/{level}/{group}/{category_id}/{subcategory_id}/{offset}"
#                 headers["referer"] = url
#                 headers["X-Requested-With"] = "XMLHttpRequest"

#                 response = None
#                 for attempt in range(3):
#                     try:
#                         response = requests.get(api_url, headers=headers, timeout=60)
#                         break
#                     except requests.exceptions.ReadTimeout:
#                         logging.warning(f"Timeout attempt {attempt+1}/3 for {api_url}")
#                         time.sleep(5)
#                     except requests.exceptions.ConnectionError:
#                         logging.warning(f"Connection error attempt {attempt+1}/3 for {api_url}")
#                         time.sleep(5)

#                 if not response or response.status_code != 200 or not response.text.strip():
#                     logging.info("Pagination completed / request failed")
#                     break

#                 if not self.parse_item(response, meta):
#                     logging.info("No more products")
#                     break

#                 offset += 24
#                 meta["offset"] = offset
#                 time.sleep(0.8)

#     def fetch_category_page(self, url, meta):
#         """Scrape products from the category page itself"""
#         try:
#             response = requests.get(url, headers=headers, timeout=60)
#         except Exception as e:
#             logging.error(f"Failed to fetch category page {url}: {e}")
#             return

#         if response.status_code == 200:
#             logging.info(f"Parsing first page of category: {url}")
#             self.parse_item(response, meta)
#         else:
#             logging.warning(f"Failed to fetch first page: {url}")

#     def parse_item(self, response, meta):
#         """Parse product items"""
#         sel = Selector(response.text)
#         PRODUCT_XPATH = '//div[contains(@class,"product")]'
#         URL_XPATH = './/a[contains(@href,"/products/view")]/@href'
#         NAME_XPATH = './/a[contains(@href,"/products/view")]/@data-productname | .//img/@alt'

#         products = sel.xpath(PRODUCT_XPATH)
#         if not products:
#             return False

#         new_urls = set()

#         for product in products:
#             url = product.xpath(URL_XPATH).get()
#             if not url:
#                 continue

#             full_url = urljoin(BASE, url)
#             if full_url in meta["seen"]:
#                 continue

#             meta["seen"].add(full_url)
#             new_urls.add(full_url)

#             name = product.xpath(NAME_XPATH).get() or ""
#             item = {
#                 "product_url": full_url,
#                 "name": name.strip(),
#                 "category": meta["category"],
#                 "offset": meta["offset"],
#             }
#             logging.info(item)
#             try:
#                 self.mongo[MONGO_COLLECTION_CATEGORY].insert_one(item)
#             except Exception as e:
#                 logging.error(e)

#         return bool(new_urls)

#     def close(self):
#         self.client.close()


# if __name__ == "__main__":
#     crawler = Crawler()
#     crawler.start()
#     crawler.close()






import logging
import time
import requests
from parsel import Selector
from pymongo import MongoClient
from urllib.parse import urlparse, urljoin
from settings import headers, MONGO_DB, MONGO_COLLECTION_CATEGORY

BASE = "https://www.portwest.com"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s"
)


class Crawler:
    """Crawling URLs from Portwest"""

    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.mongo = self.client[MONGO_DB]

    def start(self):
        """Fetch homepage and extract category URLs"""
        response = requests.get(BASE, headers=headers, timeout=30)
        if response.status_code != 200:
            logging.error("Failed to fetch homepage")
            return

        sel = Selector(text=response.text)
        category_urls = sel.xpath('//div[@class="menu-title"]/a/@href').getall()
        category_urls = [urljoin(BASE, url) for url in category_urls]

        for cat_url in category_urls:
            if "/products/" not in cat_url:
                continue

            logging.info(f"Processing category: {cat_url}")

            # Example path:
            # /products/clothing/X/1/10
            parts = urlparse(cat_url).path.strip("/").split("/")

            if len(parts) < 5:
                logging.warning(f"Invalid category URL: {cat_url}")
                continue

            # ✅ EXACT LOGIC YOU ASKED FOR
            level = parts[2]        # X
            group = parts[3]        # 1
            category_id = parts[4]  # 10

            # Skip promo / non-numeric categories
            if not group.isdigit() or not category_id.isdigit():
                logging.warning(f"Skipping non-numeric category: {cat_url}")
                continue

            meta = {
                "category": cat_url,
                "offset": 0,
                "seen": set()
            }

            # 🔹 FIRST PAGE (HTML)
            self.fetch_category_page(cat_url, meta)

            # 🔹 AJAX PAGINATION (STARTS FROM 24)
            offset = 24

            while True:
                api_url = (
                    f"{BASE}/products/load_more_category_products/"
                    f"{level}/{group}/{category_id}/{offset}"
                )

                logging.info(f"Fetching: {api_url}")

                try:
                    r = requests.get(api_url, headers=headers, timeout=30)
                except Exception as e:
                    logging.warning(f"Request error: {e}")
                    break

                if r.status_code != 200 or not r.text.strip():
                    logging.info(f"Pagination finished at offset {offset}")
                    break

                new_count = self.parse_item(r, meta)
                if new_count == 0:
                    logging.info("No more new products")
                    break

                offset += 24
                meta["offset"] = offset
                time.sleep(0.8)

    def fetch_category_page(self, url, meta):
        """Parse first HTML category page"""
        try:
            r = requests.get(url, headers=headers, timeout=30)
        except Exception as e:
            logging.error(f"Failed category page {url}: {e}")
            return

        if r.status_code == 200:
            logging.info(f"Parsing first page of category: {url}")
            self.parse_item(r, meta)

    def parse_item(self, response, meta):
        """Parse products and insert into Mongo"""
        sel = Selector(response.text)

        # ---------------- XPATHS (SEPARATE AS REQUESTED) ----------------
        PRODUCT_XPATH = '//div[contains(@class,"product")]'
        URL_XPATH = './/a[contains(@href,"/products/view")]/@href'
        NAME_XPATH = (
            './/a[contains(@href,"/products/view")]/@data-productname'
            ' | .//img/@alt'
        )

        products = sel.xpath(PRODUCT_XPATH)
        if not products:
            return 0

        inserted = 0

        for product in products:
            url = product.xpath(URL_XPATH).get()
            if not url:
                continue

            full_url = urljoin(BASE, url)
            if full_url in meta["seen"]:
                continue

            meta["seen"].add(full_url)

            name = product.xpath(NAME_XPATH).get() or ""

            item = {
                "product_url": full_url,
                "name": name.strip(),
                "category": meta["category"],
                "offset": meta["offset"],
            }

            logging.info(item)

            try:
                self.mongo[MONGO_COLLECTION_CATEGORY].insert_one(item)
                inserted += 1
            except Exception as e:
                logging.error(e)

        return inserted

    def close(self):
        self.client.close()


if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()
