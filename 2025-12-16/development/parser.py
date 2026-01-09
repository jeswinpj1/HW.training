import json
import logging
from curl_cffi import requests
from parsel import Selector
from settings import URL, HEADERS, MONGO_COLLECTION_DATA


class Parser:
    """HDCA State JSON parser"""

    def __init__(self):
        self.queue = None   # queue connection (if needed later)
        self.mongo = None   # mongo connection (inject externally)
        self.success = 0
        self.fail = 0

    def start(self):
        """start code"""

        # Example input source (same pattern as template)
        metas = [{'url': URL}]

        for meta in metas:
            url = meta.get("url")
            if not url:
                continue

            try:
                response = requests.get(
                    url,
                    headers=HEADERS,
                    impersonate="chrome",
                    timeout=20
                )

                logging.info(f"Fetching: {url} | Status: {response.status_code}")

                if response and response.status_code == 200:
                    self.parse_item(url, response)
                else:
                    self.fail += 1

            except Exception as e:
                logging.error(f"Request error for {url}: {e}")
                self.fail += 1

        logging.info(
            f"Completed | Success: {self.success} | Fail: {self.fail}"
        )

    def parse_item(self, url, response):
        """item part"""

        sel = Selector(text=response.text)

        # -------------------------
        # EXTRACT hdca-state JSON
        # -------------------------
        script_json = sel.xpath("//script[@id='hdca-state']/text()").get()

        if not script_json:
            logging.warning("hdca-state script NOT found")
            self.fail += 1
            return

        try:
            data = json.loads(script_json)
        except Exception as e:
            logging.error(f"JSON load error: {e}")
            self.fail += 1
            return

        # -------------------------
        # PRODUCT DATA LOGIC (UNCHANGED)
        # -------------------------
        product_id = list(data.keys())[0]
        product = data[product_id].get("b", {})

        product_name = product.get("name", "").strip()
        price = product.get("price", {}).get("formattedValue")
        currency = product.get("price", {}).get("currencyIso")

        if not product_name or not price:
            logging.warning("Product details NOT found")
            self.fail += 1
            return

        # -------------------------
        # ITEM YIELD (MATCH TEMPLATE)
        # -------------------------
        item = {}
        item["website"] = "HomeDepot"
        item["url"] = url
        item["product_id"] = product_id
        item["product_name"] = product_name
        item["price"] = price
        item["currency"] = currency

        logging.info(item)
        self.success += 1

        # Mongo insert (same as template)
        try:
            self.mongo.process(item, collection=MONGO_COLLECTION_DATA)
        except Exception:
            pass

    def close(self):
        """connection close"""

        if self.mongo:
            self.mongo.close()
        if self.queue:
            self.queue.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()
