import logging
import requests
from parsel import Selector
from pymongo import MongoClient
from settings import headers, MONGO_DB, MONGO_COLLECTION_CATEGORY, MONGO_COLLECTION_DATA

class Parser:
    """Portwest product parser"""

    def __init__(self):
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.mongo = self.mongo_client[MONGO_DB]

    def start(self):
        """Start parsing products"""

        # Fetch product URLs from crawler collection if available
        metas = list(self.mongo[MONGO_COLLECTION_CATEGORY].find({}, {"product_url": 1}))
        logging.info(f"Fetched {len(metas)} product URLs from MongoDB")

        if not metas:
            logging.warning("No product URLs found in MongoDB")
            return

        for meta in metas:
            url = meta.get("product_url")
            if not url:
                continue

            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    self.parse_item(url, response)
                else:
                    logging.warning(f"Failed to fetch {url}, status: {response.status_code}")
            except Exception as e:
                logging.error(f"Error fetching {url}: {e}")

    def parse_item(self, url, response):
        """Parse product details"""

        sel = Selector(text=response.text)

        # ---------------- XPATH ----------------
        PRODUCT_NAME_XPATH = '//h2/text()'
        COLOUR_XPATH = '//div[@class="ratings-container"]//h2/text()'
        IMAGES_XPATH = '//img[@class="product-single-image"]/@src'
        COLOUR_VARIANTS_XPATH = '//ul[@class="config-swatch-list"]/li/a'
        SIZE_XPATH = '//label[contains(text(),"Size Range")]/following-sibling::div/text()'
        DESCRIPTION_XPATH = '//p[@class="text-justify"]/text()'
        FEATURES_XPATH = '//section[@id="content3"]//li/text()'
        SHELL_FABRIC_XPATH = '//div[contains(text(),"Shell Fabric")]/following-sibling::div/text()'
        DOCUMENTS_XPATH = '//section[@id="content4"]//a'
        WASHCARE_XPATH = '//table//img'

        # ---------------- EXTRACT ----------------
        def clean(text):
            return text.strip() if text else None

        product_name = clean(sel.xpath(PRODUCT_NAME_XPATH).get())
        colour = clean(sel.xpath(COLOUR_XPATH).get())
        style_code = product_name.split("-")[0].strip() if product_name and "-" in product_name else None

        images = list(set(sel.xpath(IMAGES_XPATH).getall()))
        colour_variants = []
        for a in sel.xpath(COLOUR_VARIANTS_XPATH):
            colour_variants.append({
                "url": a.xpath('@href').get(),
                "image": a.xpath('.//img/@src').get()
            })

        size_range = clean(sel.xpath(SIZE_XPATH).get())
        description = clean(sel.xpath(DESCRIPTION_XPATH).get())
        features = [clean(f) for f in sel.xpath(FEATURES_XPATH).getall() if clean(f)]
        shell_fabric = clean(sel.xpath(SHELL_FABRIC_XPATH).get())

        documents = {}
        for a in sel.xpath(DOCUMENTS_XPATH):
            key = clean(a.xpath('text()').get())
            link = a.xpath('@href').get()
            if key and link:
                documents[key.lower().replace(" ", "_")] = link

        washcare = []
        for img in sel.xpath(WASHCARE_XPATH):
            washcare.append({
                "icon": img.xpath('@src').get(),
                "title": img.xpath('@title').get()
            })

        # ---------------- ITEM ----------------
        item = {
            "brand": "Portwest",
            "product_name": product_name,
            "style_code": style_code,
            "mpn": style_code,
            "gtin": None,
            "uom": None,
            "quantity": None,
            "intrastat_code": None,
            "pdp_url": url,
            "colour": colour,
            "size_range": size_range,
            "description": description,
            "features": features,
            "shell_fabric": shell_fabric,
            "images": images,
            "colour_variants": colour_variants,
            "documents": documents,
            "washcare": washcare
        }

        logging.info(item)

        try:
            self.mongo[MONGO_COLLECTION_DATA].insert_one(item)
        except Exception as e:
            logging.error(f"Mongo insert failed: {e}")

    def close(self):
        """Close Mongo connection"""
        self.mongo_client.close()


if __name__ == "__main__":
    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()
