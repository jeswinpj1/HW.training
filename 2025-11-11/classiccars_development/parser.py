import logging
import time
import requests
from parsel import Selector
from pymongo import MongoClient
from mongoengine import connect

from item import ClassicCarItem
from settings import HEADERS, COOKIES, MONGO_COLLECTION_URLS, MONGO_COLLECTION_DATA, MONGO_DB_NAME, MONGO_URI

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")


class ClassicCarsParser:
    """Parser for classiccars.com listings"""

    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.urls_collection = self.db[MONGO_COLLECTION_URLS]
        self.data_collection = self.db[MONGO_COLLECTION_DATA]
        self.session = requests.Session()
        self.success = 0
        self.failure = 0
        connect(db=MONGO_DB_NAME, host=MONGO_URI)

    def get_clean_urls(self):
        """Fetch and clean URLs stored in MongoDB"""
        urls = []
        for doc in self.urls_collection.find({}, {"url": 1, "_id": 0}):
            url = doc.get("url", "").strip()
            if not url:
                continue
            # Clean malformed URLs like "classiccars.comhttps://"
            if "classiccars.comhttps://" in url:
                url = "https://" + url.split("classiccars.comhttps://")[-1]
            urls.append(url)
        return urls

    def start(self):
        """Main entry: fetch, parse, and save"""
        urls = self.get_clean_urls()
        total = len(urls)
        logging.info(f"Processing {total} URLs...\n")

        for idx, url in enumerate(urls, start=1):
            logging.info(f"[{idx}/{total}] Fetching: {url}")
            try:
                response = self.session.get(url, headers=HEADERS, cookies=COOKIES, timeout=20)
                if response.status_code == 200:
                    self.parse_item(url, response)
                else:
                    self.failure += 1
                    logging.warning(f"Failed ({response.status_code}): {url}")
            except Exception as e:
                self.failure += 1
                logging.error(f"Error fetching {url}: {e}")

            time.sleep(0.5)

        self.summary()

    def parse_item(self, url, response):
        """Extract product data and store to Mongo"""
        sel = Selector(text=response.text)

        image_urls = [
            img if img.startswith("http") else f"https://classiccars.com{img}"
            for img in sel.xpath('//div[@id="MCThumbsRapper"]//img/@src | //div[@id="MCThumbsRapper"]//img/@data-src').getall()]

        description = " ".join([d.strip() for d in sel.xpath('//div[contains(@class,"description")]//text()').getall() if d.strip()])

        item_data = {
            "source_url": url,
            "make": sel.xpath('//li[contains(@class,"p-manufacturer")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "model": sel.xpath('//li[contains(@class,"p-model")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "year": sel.xpath('//li[contains(@class,"dt-start")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "VIN": sel.xpath('//li[contains(@class,"p-vin")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "price": sel.xpath('//li[contains(@class,"p-price")]//span[contains(@class,"red")]/text()').get(default="").strip(),
            "mileage": sel.xpath('//li[contains(@class,"p-odometer")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "transmission": sel.xpath('//li[contains(@class,"p-transmission")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "engine": sel.xpath('//li[contains(@class,"p-engine")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "color": sel.xpath('//li[contains(@class,"p-color")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "fuel_type": "",
            "body_style": "",
            "description": description,
            "image_urls": image_urls,
        }
        # Check for duplicate
        if ClassicCarItem.objects(source_url=url).first():
            logging.info(f"Duplicate skipped: {url}")
            return
        try:
            item = ClassicCarItem(**item_data)
            item.validate()
            item.save()
            self.success += 1
            logging.info(f"Saved item: {url}")
        except Exception as e:
            self.failure += 1
            logging.warning(f"Skipping invalid data ({url}): {e}")

    def close(self):
        self.session.close()
        self.client.close()
        logging.info("Parser closed.")

if __name__ == "__main__":
    parser = ClassicCarsParser()
    parser.start()
    parser.close()
