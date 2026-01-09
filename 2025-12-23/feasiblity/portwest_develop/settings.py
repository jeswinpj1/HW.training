from datetime import datetime
import os
import calendar
import logging
import configparser
import pytz
from dateutil.relativedelta import relativedelta, MO
import requests

# ----------------------------
# LOGGING
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ----------------------------
# BASIC DETAILS
# ----------------------------
PROJECT = "portwest"
CLIENT_NAME = "portwest"
PROJECT_NAME = "portwest"
FREQUENCY = "adhoc"
BASE_URL = "https://www.portwest.com"

# ----------------------------
# DATE / ITERATION
# ----------------------------
datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))

iteration = datetime_obj.strftime("%Y_%m_%d")
YEAR = datetime_obj.strftime("%Y")
MONTH = datetime_obj.strftime("%m")
DAY = datetime_obj.strftime("%d")
MONTH_VALUE = calendar.month_abbr[int(MONTH.lstrip("0"))]
WEEK = (int(DAY) - 1) // 7 + 1

FILE_NAME = f"portwest_{iteration}"

# ----------------------------
# MONGO DB & COLLECTIONS
# ----------------------------
MONGO_DB = f"portwest_{iteration}"

MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_response"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_url"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_PRODUCT_URLS = f"{PROJECT_NAME}_product_urls"

# ----------------------------
# PROXY
# ----------------------------
PROXY = ""

# ----------------------------
# QUEUE DETAILS
# ----------------------------
QUEUE_NAME_URL = f"{PROJECT_NAME}_urls"
QUEUE = ""

# ----------------------------
# SHARD / INDEX DETAILS
# ----------------------------
MONGO_COL_URL = f"{PROJECT_NAME}_url"

SHARD_COLLECTION = [
    {
        "col": MONGO_COL_URL,
        "unique": True,
        "indexfield": "url"
    }
]

# ----------------------------
# HEADERS
# ----------------------------
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "text/html, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "X-Requested-With": "XMLHttpRequest",
}
