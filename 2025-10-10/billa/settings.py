import re
import time
import logging
import requests
from parsel import Selector
from pymongo import MongoClient
from datetime import datetime

from datetime import datetime 
import pytz 
import logging 
# ----------------- Logging ----------------- 
logging.basicConfig( level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S", ) 
# ----------------- Project Info ----------------- 
PROJECT = "billa_scraper"
PROJECT_NAME = "billa" 
CLIENT_NAME = "Billa" # use "Billa_test"
BASE_URL = "https://shop.billa.at/" 
# STORE_ID = "00-10"
REQUEST_DELAY = 0.5 # seconds between API requests 
TOTAL_PAGES = 352
PAGE_SIZE = 30
 # ----------------- Extraction Date -----------------
datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata")) 
EXTRACTION_DATE = datetime_obj.strftime("%Y-%m-%d") 
FILE_NAME_FULLDUMP = f"_Billa_corrected_{datetime_obj:%Y%m%d}.CSV" 
# ----------------- MongoDB ----------------- 
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "billa_scraper" 
MONGO_COLLECTION_DATA = "product_data" 
MONGO_COLLECTION_ENRICHED_DATA = "full126_product_data"
MONGO_COLLECTION_URL_FAILED = "billa_url_failed"
MONGO_COLLECTION_CATEGORY = "billa_category_url" 
# ----------------- Headers ----------------- 
HEADERS_PAGE = { "User-Agent": ( "Mozilla/5.0 (X11; Linux x86_64) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/141.0.0.0 Safari/537.36" ), "Accept": "application/json" } 
# ----------------- API ----------------- 
API_URL = "https://shop.billa.at/api/product-discovery/products?count=30&offset=0" 
# ----------------- Grammage ----------------- 
GRAMMAGE_REGEX = r'(\d+(?:[.,]\d+)?)(?:\s?x\s?\d+(?:[.,]\d+)?)?\s?(ml|l|g|kg|cl|dl|oz|lt|pcs|st|stück)\b'
# ----------------- CSV -----------------
CSV_DELIMITER = "|" 
CSV_QUOTECHAR = '"' 
#API_URL = "https://shop.billa.at/api/product-discovery/products"