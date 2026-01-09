# settings.py

from datetime import datetime
import calendar
import pytz
import logging

# ------------------------------------------------
# LOGGING CONFIG
# ------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ------------------------------------------------
# PROJECT DETAILS (EDIT THESE)
# ------------------------------------------------
PROJECT = "homedepot"
CLIENT_NAME = "internal"
PROJECT_NAME = "homedepot_ca"
FREQUENCY = "monthly"

BASE_URL = "https://www.homedepot.ca/"

# ------------------------------------------------
# DATE & ITERATION DETAILS
# ------------------------------------------------
IST_TIMEZONE = pytz.timezone("Asia/Kolkata")
NOW = datetime.now(IST_TIMEZONE)

ITERATION = NOW.strftime("%Y_%m_%d")
YEAR = NOW.strftime("%Y")
MONTH = NOW.strftime("%m")
DAY = NOW.strftime("%d")

MONTH_VALUE = calendar.month_abbr[int(MONTH)]
WEEK = (int(DAY) - 1) // 7 + 1

FILE_NAME = f"{PROJECT_NAME}_{ITERATION}"

# ------------------------------------------------
# MONGO DATABASE CONFIG
# ------------------------------------------------
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = f"{PROJECT_NAME}_{ITERATION}"

MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category"
MONGO_COLLECTION_PRODUCT = f"{PROJECT_NAME}_product_urls"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_FAILED = f"{PROJECT_NAME}_failed_urls"

# ------------------------------------------------
# QUEUE CONFIG (OPTIONAL)
# ------------------------------------------------
QUEUE_NAME_URL = f"{PROJECT_NAME}_urls"
QUEUE = None  # Redis / RabbitMQ connection placeholder

# ------------------------------------------------
# PROXY (OPTIONAL)
# ------------------------------------------------
PROXY = None

# ------------------------------------------------
# REQUEST HEADERS
# ------------------------------------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
    "Connection": "keep-alive",
}

# ------------------------------------------------
# CRAWLER SETTINGS
# ------------------------------------------------
REQUEST_TIMEOUT = 30
DOWNLOAD_DELAY = 1.5
MAX_RETRIES = 3
