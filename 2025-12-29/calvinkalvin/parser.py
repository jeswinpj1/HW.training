import logging
import requests
from parsel import Selector
from settings import HEADERS, MONGO_COLLECTION_DATA, BASE_URL
from pymongo import MongoClient
import re
import json
from urllib.parse import urlparse
import os
class Parser:
    """Calvin Klein Product Parser"""

    def __init__(self):
        # MongoDB connection
        self.mongo = MongoClient("mongodb://localhost:27017")
        self.db = self.mongo["calvinklein"]
        self.collection = self.db[MONGO_COLLECTION_DATA]

    def start(self):
        """Fetch product URLs from MongoDB and parse"""

        product_urls = self.db["product_urls"].find()  # product URLs already saved by crawler

        for product in product_urls:
            url = product.get("product_url")
            try:
                response = requests.get(url, headers=HEADERS)
                if response.status_code == 200:
                    self.parse_item(url, response)
                else:
                    logging.warning(f"Failed to fetch {url}")
            except Exception as e:
                logging.error(f"Error fetching {url}: {e}")

    def close(self):
        """Close MongoDB connection"""
        self.mongo.close()

    def parse_item(self, url, response):
        """Extract product details from Calvin Klein PDP page"""

        sel = Selector(text=response.text)

        # ---------------- XPATHS ----------------
        breadcrumbs_xpath = '//div[@class="ds-breadcrumb-desktop"]//ul/li/a/text()'
        product_name_xpath = '//div[@class="buy-box__name"]/h1[@class="product-name"]/text()'
        original_price_xpath = '//div[contains(@class,"price")]/del//span[@class="value"]/@content'
        sale_price_xpath = '//div[contains(@class,"price")]//span[@class="sales"]/span[@class="value"]/@content'
        discount_xpath = '//div[contains(@class,"price")]//span[@class="ds-discount"]/span/text()'
        rating_xpath = '//div[@id="tt-teaser-reviews"]//span[@class="tt-reviews-avgRating"]/text()'
        total_reviews_xpath = '//div[@id="tt-teaser-reviews"]//span[contains(@class,"TTteaser__read-reviews-panel")]/text()'
        color_keyvalue_xpath = '//ul[contains(@class,"variant-list--colorCode")]//li//span[@aria-label]/@aria-label'
        color_urls_xpath = '//ul[contains(@class,"variant-list--colorCode")]//li/input/@data-url'
        # sizes_xpath = '//div[contains(@class,"variant-list") and @data-display-id="size"]//input/@data-attr-value'
        sizes_xpath = (
            '//div[contains(@class,"variant-list") and @data-display-id="size"]//input/@data-attr-value | '
            '//div[contains(@class,"variant-list") and @data-display-id="waist"]//input/@data-attr-value'
        )

        # colors_xpath = '//h3[contains(@class,"colorCode")]//span[@class="variation__attr--value"]/text()'
        size_urls_xpath = '//div[contains(@class,"variant-list") and @data-display-id="size"]//input/@data-url'
        features_xpath = '//div[contains(@class,"product-detail__attributes")]//div[contains(@class,"buy-box__attribute")]/h3//span[@class="variation__attr--name"]/text() | //div[contains(@class,"product-detail__attributes")]//div[contains(@class,"buy-box__attribute")]/h3//span[@class="variation__attr--value"]/text()'
        about_xpath = '//div[@class="description-and-detail"]//div[@class="content-block"][h2/text()="About"]/div[@class="content-description"]/text()'
        features_xpath = '//div[contains(@class,"content-block no-margin")][h2[contains(text(),"Details")]]//ul[contains(@class,"content-list")]/li/text()'
        table_xpath = '//div[contains(@class,"content-block no-margin")][h2[contains(text(),"Details")]]//ul[contains(@class,"content-table")]/li[contains(@class,"content-row")]'
    
        # ---------------- EXTRACT ----------------
        product_name = sel.xpath(product_name_xpath).get()
        product_name = product_name.strip() if product_name else ""

        brand = "Calvin Klein"
        currency = "USD"

        # ---------------- DESCRIPTION ----------------
        
        description = sel.xpath(about_xpath).get()
        description = description.strip() if description else ""

        # ---------------- FEATURES ----------------
        
        
        features = [f.strip() for f in sel.xpath(features_xpath).getall() if f.strip()]
        
        # XPath to select each row in the content table
        table_xpath = '//div[contains(@class,"content-block no-margin")][h2[contains(text(),"Details")]]//ul[contains(@class,"content-table")]/li[contains(@class,"content-row")]'

        table_rows = sel.xpath(table_xpath)

        table_features = []

        for row in table_rows:
            # Use string() to get all text content inside the div
            label = row.xpath('.//div[contains(@class,"content-column")][1]//text()').get()
            value = row.xpath('.//div[contains(@class,"content-column")][2]//text()').get()
            
            if label and value:
                table_features.append(f"{label.strip()}: {value.strip()}")

        original_price = sel.xpath(original_price_xpath).get()
        sale_price = sel.xpath(sale_price_xpath).get()
        original_price = original_price.strip() if original_price else ""
        sale_price = sale_price.strip() if sale_price else original_price

        features = sel.xpath(features_xpath).getall()
        features = [f.strip() for f in features if f.strip()] if features else []

        colors = sel.xpath(color_keyvalue_xpath).getall()
        colors = [c.strip() for c in colors if c.strip()] if colors else []

        sizes = sel.xpath(sizes_xpath).getall()
        sizes = [s.strip() for s in sizes if s.strip()] if sizes else []

        breadcrumbs_list = sel.xpath(breadcrumbs_xpath).getall()
        category = ">".join([b.strip() for b in breadcrumbs_list if b.strip()])

        # ---------------- SKU ----------------
        path = urlparse(url).path  # e.g., /en/women/apparel/tops/mouline-rib-cardigan/47E331G-5FZ.html
        product_sku = os.path.basename(path).replace(".html", "")  # 47E331G-5FZ

        # ---------------- Reviews & Rating ----------------
        total_reviews, rating = self.fetch_reviews(product_sku)

        # ---------------- ITEM ----------------
        item = {
            "url": url,
            "product_sku": product_sku,
            "product_name": product_name,
            "brand": brand,
            "currency": currency,
            "original_price": original_price,
            "sale_price": sale_price,
            "category": category,
            "total_number_of_reviews": total_reviews,
            "rating": rating,
            "description": description,
            "features": features,
            "table_features": table_features,
            "color": colors,
            "size": sizes,
        }

        logging.info(item)
        try:
            self.collection.insert_one(item)
        except Exception as e:
            logging.warning(f"Failed to insert: {e}")


    def fetch_reviews(self, sku):
        """Fetch rating and review count from TurnTo API"""

        if not sku:
            return 0, 0.0

        try:
            review_url = f"https://cdn-ws.turnto.com/v5/sitedata/VKDc5zpcAisPzdtsite/{sku}/d/ugc/counts/en_US"
            response = requests.get(review_url, headers=HEADERS, timeout=5)
            if response.status_code == 200:
                data = response.json()
                total_reviews = data.get("reviews", 0)
                rating = data.get("avgRating", 0.0)
                return total_reviews, rating
        except Exception as e:
            logging.warning(f"Failed to fetch reviews for SKU {sku}: {e}")

        return 0, 0.0



if __name__ == "__main__":
    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()
