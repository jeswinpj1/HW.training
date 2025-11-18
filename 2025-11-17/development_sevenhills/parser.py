import logging
import requests
import time
from parsel import Selector
from mongoengine import connect
from items import ProductItem
from settings import HEADERS, MONGO_URI, MONGO_DB, MONGO_COLLECTION_URL
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

connect(host=MONGO_URI, db=MONGO_DB, alias="default")

class Parser:
    def __init__(self):
    
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        try:
            self.session.get("https://www.sevenhillsmotorcars.com/", timeout=10)
        except Exception as e:
            logging.warning(f"Initial session request failed: {e}")

        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        doc = db[MONGO_COLLECTION_URL].find_one({"category_url": "vehicles_all"})
        client.close()

        if not doc:
            logging.warning("No URL document found for 'vehicles_all'")
            self.current_urls = []
            self.sold_urls = []
        else:
            self.current_urls = doc.get("current", [])
            self.sold_urls = doc.get("sold", [])

        logging.info(
            f"Fetched {len(self.current_urls)} current and {len(self.sold_urls)} sold URLs"
        )

    def parse_item(self, url):
        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 403:
                logging.warning(f"403 for {url}, retrying after 5 sec...")
                time.sleep(5)
                resp = self.session.get(url, timeout=15)

            if resp.status_code != 200:
                logging.warning(f"Failed: {url} (Status {resp.status_code})")
                return

            sel = Selector(resp.text)
            page_title = sel.xpath(
                "normalize-space(//h1/text() | //title/text())"
            ).get(default="").split("|")[0].strip()

            year, make, model = "N/A", "N/A", "N/A"
            parts = page_title.split(" ", 3)
            if parts and parts[0].isdigit():
                year = parts[0]
                if len(parts) > 1: make = parts[1]
                if len(parts) > 2: model = parts[2]

            item = ProductItem(
                url=url,
                make=make,
                model=model,
                year=year,
                vin=sel.xpath('normalize-space(//dt[contains(., "Vin")]/following-sibling::dd/text())').get(default=""),
                stock_no=sel.xpath('normalize-space(//dt[contains(., "Stock")]/following-sibling::dd/text())').get(default=""),
                price=sel.xpath('normalize-space(//dt[contains(., "Price")]/following-sibling::dd/text())').get(default="Call for Price"),
                mileage=sel.xpath('normalize-space(//dt[contains(., "Miles")]/following-sibling::dd/text())').get(default=""),
                transmission=sel.xpath('normalize-space(//dt[contains(., "Transmission")]/following-sibling::dd/text())').get(default=""),
                engine=sel.xpath('normalize-space(//dt[contains(., "Engine")]/following-sibling::dd/text())').get(default=""),
                exterior_color=sel.xpath('normalize-space(//dt[contains(., "Exterior")]/following-sibling::dd/text())').get(default=""),
                interior_color=sel.xpath('normalize-space(//dt[contains(., "Interior")]/following-sibling::dd/text())').get(default=""),
                body_style=sel.xpath('normalize-space(//dt[contains(., "Body Style")]/following-sibling::dd/text())').get(default=""),
                description=sel.xpath('normalize-space(//div[contains(@id,"description") or contains(@class,"vehicle-description")])').get(default=""),
                image_urls=sel.xpath('//div[@id="show-car-thumbs"]/a/@data-original').getall())

            item.save()
            logging.info(f"Saved: {url}")

        except Exception as e:
            logging.error(f"Error parsing {url}: {e}")

    def run(self):
        try:
            # Process current vehicles
            logging.info("Parsing CURRENT vehicles...")
            for i, url in enumerate(self.current_urls, start=1):
                logging.info(f"[{i}/{len(self.current_urls)}] {url}")
                self.parse_item(url)
                time.sleep(1.5)

            # Process sold vehicles
            logging.info("Parsing SOLD vehicles...")
            for i, url in enumerate(self.sold_urls, start=1):
                logging.info(f"[{i}/{len(self.sold_urls)}] {url}")
                self.parse_item(url)
                time.sleep(1.5)

        finally:
            self.session.close()
            logging.info("Session closed.")

if __name__ == "__main__":
    parser = Parser()
    parser.run()


