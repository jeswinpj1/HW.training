# import logging, time, requests
# from lxml import html
# from pymongo import MongoClient, errors
# from settings import BASE_URL, LAST_PAGE, HEADERS, MONGO_URI, DB_NAME, SOURCE_COLLECTION
# from items import PropertyURL

# class WasaltScraper:
#     def __init__(self):
#         self.client = MongoClient(MONGO_URI)
#         self.collection = self.client[DB_NAME][SOURCE_COLLECTION]
#         #  Makes MongoDB automatically reject duplicate URLs
#         self.collection.create_index("url", unique=True)

#     def fetch(self, url):
#         logging.info(f"Fetching page: {url}")
#         r = requests.get(url, headers=HEADERS, timeout=30)
#         r.raise_for_status()
#         return r.text

#     def parse_urls(self, content):
#         tree = html.fromstring(content)
#         urls = tree.xpath("//div[contains(@class,'styles_cardContent')]/a/@href")
#         return ["https://wasalt.sa" + u if u.startswith("/") else u for u in urls]

#     def save(self, urls):
#         for url in urls:
#             try:
#                 item = PropertyURL(url)
#                 self.collection.insert_one(item.__dict__)
#                 logging.info(f"Saved URL: {url}")
#             except errors.DuplicateKeyError:
#                 logging.info(f"Skipped duplicate: {url}")

#     def run(self):
#         for page in range(1, LAST_PAGE + 1):
#             url = f"{BASE_URL}&page={page}"
#             try:
#                 content = self.fetch(url)
#                 urls = self.parse_urls(content)
#                 self.save(urls)
#                 time.sleep(1)
#             except Exception as e:
#                 logging.error(f"Error on page {page}: {e}")

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     WasaltScraper().run()




#...............................................................................................................................................................





from settings import BASE_URL, LAST_PAGE, HEADERS, MONGO_URI, DB_NAME, SOURCE_COLLECTION
import logging, time, requests
from parsel import Selector
from pymongo import MongoClient, errors


class Crawler:
    """Crawling URLs - Wasalt"""

    def __init__(self):
        self.queue = ''     # Optional queue support
        self.client = MongoClient(MONGO_URI)
        self.mongo = self.client[DB_NAME][SOURCE_COLLECTION]
        self.mongo.create_index("url", unique=True)  # Avoid duplicate URLs

    def start(self):
        """Start crawling pages from BASE_URL with pagination"""
        base = BASE_URL  

        for page in range(1, LAST_PAGE + 1):
            url = f"{base}&page={page}"
            logging.info(f"Fetching page: {url}")
            try:
                headers = HEADERS.copy()
                headers["referer"] = base
                response = requests.get(url, headers=headers, timeout=30)

                if response.status_code == 200:
                    is_next = self.parse_item(response, {"page": page, "category": base})
                    if not is_next:
                        logging.info("Pagination completed")
                        break
                    time.sleep(1)
                else:
                    logging.error(f"Non-200 status: {response.status_code}")
                    # self.queue.publish(url)  # Re-queue logic if needed

            except Exception as e:
                logging.error(f"Error fetching page {page}: {e}")

    def parse_item(self, response, meta):
        """Extract property listing URLs"""
        sel = Selector(response.text)

        # XPATH for property URLs
        URL_XPATH = "//div[contains(@class,'styles_cardContent')]/a/@href"
        urls = sel.xpath(URL_XPATH).getall()

        if urls:
            for url in urls:
                full_url = "https://wasalt.sa" + url if url.startswith("/") else url
                item = {
                    "url": full_url,
                    "category": meta.get("category"),
                    "page": meta.get("page")
                }
                logging.info(item)

                try:
                    self.mongo.insert_one(item)
                except errors.DuplicateKeyError:
                    logging.info(f"Duplicate skipped: {full_url}")
                except Exception as e:
                    logging.error(f"Error saving {full_url}: {e}")

            return True  # Continue to next page
        return False  # Stop pagination if no URLs

    def close(self):
        """Close DB / Queue connections"""
        try:
            self.client.close()
            # self.queue.close()
        except:
            pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    crawler = Crawler()
    crawler.start()
    crawler.close()
