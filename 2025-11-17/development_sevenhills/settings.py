
from datetime import datetime
import os
import calendar
import logging
import configparser
import pytz
from dateutil.relativedelta import relativedelta, MO
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ---------------------------
# Project Details
# ---------------------------
PROJECT = "SevenHillsMotorcars"
CLIENT_NAME = "SevenHills"
PROJECT_NAME = "sevenhills"
FREQUENCY = "Daily"
BASE_URL = "https://www.sevenhillsmotorcars.com"
MONGO_URI = "mongodb://localhost:27017/"
# ---------------------------
# Timestamp / Iteration Info
# ---------------------------
datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))

iteration = datetime_obj.strftime("%Y_%m_%d")
YEAR = datetime_obj.strftime("%Y")
MONTH = datetime_obj.strftime("%m")
DAY = datetime_obj.strftime("%d")
MONTH_VALUE = calendar.month_abbr[int(MONTH.lstrip("0"))]
WEEK = (int(DAY) - 1) // 7 + 1

FILE_NAME = f"sevenhills_{iteration}.csv"

# ---------------------------
# MongoDB Collections
# ---------------------------
MONGO_DB = f"sevenhills_2025_11_17"
MONGO_COLLECTION_URL = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_response"
MONGO_COLLECTION_PAGINATION = f"{PROJECT_NAME}_pagination"

# ---------------------------
# Headers
# ---------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/118.0.5993.90 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.sevenhillsmotorcars.com/",
}

FILE_HEADERS = [
    "url",
    "make",
    "model",
    "year",
    "vin",
    "stock_no",
    "price",
    "mileage",
    "transmission",
    "engine",
    "exterior_color",
    "interior_color",
    "body_style",
    "description",
    "image_urls"
]
