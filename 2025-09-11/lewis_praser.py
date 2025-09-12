import requests
from parsel import Selector
import re
from datetime import datetime
import pymongo
import logging
from requests.exceptions import RequestException, Timeout, HTTPError
from pymongo.errors import PyMongoError

API_KEY = "504eeef7c076dfcf401adae86875886d"
SCRAPERAPI_URL = "https://api.scraperapi.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}

logging.basicConfig(
    filename="johnlewis_parser.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["johnlewis"]
crawler_collection = db["products"]        
parser_collection = db["product_details"]  

def fetch_selector(url):
    """Fetch a URL via ScraperAPI and return a parsel.Selector"""
    try:
        response = requests.get(
            SCRAPERAPI_URL,
            params={"api_key": API_KEY, "url": url},
            headers=HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        return Selector(text=response.text)
    except (RequestException, Timeout, HTTPError) as e:
        logging.error(f"Failed to fetch {url} -> {e}")
        return None

def clean_value(value, default=""):
    """Normalize strings and lists"""
    if value is None or (isinstance(value, str) and not value.strip()):
        return default
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    if isinstance(value, list):
        cleaned = [clean_value(v, default) for v in value if v and v.strip()]
        return cleaned if cleaned else [default]
    return value

def parse_product_code(sel):
    return clean_value(sel.xpath('normalize-space(//p[@data-testid="description:code"]/strong/text())').get())

def parse_title(sel):
    return clean_value(sel.xpath("//span[@data-testid='product:title:content']/text()").get())

def parse_price(sel):
    price = sel.xpath("//span[@class='price_price__now__bNSvu']/text()").get()
    return clean_value(price.replace("£", "").strip() if price else None)

def parse_description(sel):
    desc = sel.xpath("//div[@class='ProductDescriptionAccordion_descriptionContent__yd_yu']/p/text()").getall()
    return clean_value(" ".join([d.strip() for d in desc if d.strip()]))

def parse_colors(sel):
    return clean_value(sel.xpath("//h3[@data-testid='colourlist:label']/span/text()").getall())

def parse_unique_id(sel):
    return clean_value(sel.xpath("//p[@data-testid='description:code']/strong/text()").getall())

def parse_brand(sel):
    return clean_value(sel.xpath("//span[contains(@data-testid,'product:title')]/text()").get())

def parse_product_page(product_url, category="", subcategory=""):
    sel = fetch_selector(product_url)
    if not sel:
        return None

    product_data = {
        "url": product_url,
        "category": category,
        "subcategory": subcategory,
        "title": parse_title(sel),
        "price": parse_price(sel),
        "currency": "£",
        "brand": parse_brand(sel),
        "description": parse_description(sel),
        "colors": parse_colors(sel),
        "unique_id": parse_unique_id(sel),
        "timestamp": datetime.utcnow(),
    }
    return product_data

def run_parser():
    count = 0
    try:
        for doc in crawler_collection.find():
            category_url = doc.get("category_url", "")
            for sub in doc.get("subcategories", []):
                subcategory_url = sub.get("subcategory_url", "")
                for product_url in sub.get("product_urls", []):
                    logging.info(f"Parsing {product_url}")
                    data = parse_product_page(product_url, category=category_url, subcategory=subcategory_url)
                    if data:
                        parser_collection.insert_one(data)
                        count += 1
        logging.info(f"Inserted {count} product docs into 'product_details'")
    except PyMongoError as e:
        logging.error(f"MongoDB error: {e}")

if __name__ == "__main__":
    run_parser()
