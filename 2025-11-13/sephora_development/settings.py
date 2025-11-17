import logging
import time
import urllib.parse
from datetime import datetime
import pytz
import calendar
from pymongo import MongoClient

# --- Date & Project Setup ---
datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))
iteration = datetime_obj.strftime("%Y_%m_%d")
PROJECT_NAME = "sephora_sg"

# --- MongoDB Collections (Dynamic Naming) ---
MONGO_DB_NAME = f"{PROJECT_NAME}_{iteration}"

MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_url"           # Stores product URLs
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"  # Stores category URLs
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"             # Stores final parsed data
MONGO_COLLECTION_PAGINATION = f"{PROJECT_NAME}_pagination"

# --- Configuration ---
BASE_URL = "https://www.sephora.sg"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-SG",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "x-app-platform": "web_desktop",
    "x-app-version": "1.0.0",
    "x-platform": "web",
    "x-requested-with": "XMLHttpRequest",
    "x-site-country": "SG",
    "origin": "https://www.sephora.sg",
    "referer": "https://www.sephora.sg/",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    ),
}
POLITE_DELAY = 2  # seconds

# --- MongoDB Client ---
client = MongoClient("mongodb://localhost:27017/")
db = client[MONGO_DB_NAME]

# --- Collections Objects ---
collection_categories = db[MONGO_COLLECTION_CATEGORY]
collection_products = db[MONGO_COLLECTION_DATA]

file_name = f"{PROJECT_NAME}_{iteration}.csv"

# --- XPaths ---
MAIN_CATEGORY_BLOCKS_XPATH = '//div[contains(@class, "menu-dropdown")][.//div[contains(@class, "categories-dropdown-container")]]'
MAIN_CATEGORY_NAME_XPATH = './/div[contains(@class, "dropdown-trigger")]//div[contains(@class, "text-container")]/text()'
SUB_CATEGORY_LINKS_XPATH = './/div[contains(@class, "categories-dropdown-container")]//a[starts-with(@href, "/categories/")]'
PRODUCT_URL_XPATH = '//a[contains(@class, "product-card-description")]/@href'
NEXT_PAGE_XPATH = '//a[contains(@class, "pagination-item") and contains(@class, "next-page")]/@href'

BASE_API = "https://www.sephora.sg/api/v2.6/products/"
INCLUDE_PARAMS = (
    "variants.filter_values,variants.ingredient_preference,"
    "featured_ad.virtual_bundle.bundle_elements,product_articles,filter_types"
)

FILE_HEADERS = [
    "retailer_id",
    "retailer",
    "product_name",
    "brand",
    "grammage_quantity",
    "grammage_unit",
    "original_price",
    "selling_price",
    "promotion_description",
    "pdp_url",
    "image_url",
    "ingredients",
    "directions",
    "disclaimer",
    "description",
    "diet_suitability",
    "colour",
    "hair_type",
    "skin_type",
    "skin_tone"
]