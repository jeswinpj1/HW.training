import logging
import time
import requests
from parsel import Selector
from pymongo import MongoClient, errors

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "2025-10-20_wasalt"
SOURCE_COLLECTION = "properties_urls"        
TARGET_COLLECTION = "property_details"   

BASE_URL = "https://wasalt.sa/en/sale/search?countryId=1&propertyFor=sale&type=residential"
LAST_PAGE = 689


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
