import logging
import pytz
from datetime import datetime
import calendar

# --- 1. Basic Configuration ---
PROJECT = "Lidl"
CLIENT_NAME = "Client_Name"
PROJECT_NAME = "lidl_2025_12"
FREQUENCY = "Daily"
BASE_URL = "https://www.lidl.co.uk/"

# --- 2. Logging Setup (Simple) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# --- 3. Date & Iteration Variables ---
datetime_obj = datetime.now(pytz.timezone("UTC"))

# Simple date strings
ITERATION = datetime_obj.strftime("%Y_%m_%d")
YEAR = datetime_obj.strftime("%Y")
MONTH = datetime_obj.strftime("%m")
DAY = datetime_obj.strftime("%d")
MONTH_VALUE = calendar.month_abbr[int(MONTH)]
WEEK = (int(DAY) - 1) // 7 + 1

FILE_NAME = f"lidl_2025_12_12_sample_data.csv"


# --- 4. MongoDB and Collections ---
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = f"{PROJECT_NAME}_{ITERATION}"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_DATA_FULL = f"{PROJECT_NAME}_data_full"
MONGO_COLLECTION_CATEGORY = f"{PROJECT_NAME}_category_id"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_URL = f"{PROJECT_NAME}_pdp_url" # For Product Detail Page URLs

# --- 5. Queue and Proxy (Placeholders) ---
QUEUE_NAME_URL = f"{PROJECT_NAME}_urls_queue"
QUEUE = None
PROXY = None

# --- 6. Headers (Based on your Lidl API script) ---
HEADERS = {
    "Accept": "application/mindshift.search+json;version=2",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Referer": BASE_URL,
}

# --- 7. Shard/Index Configuration (Example) ---
SHARD_COLLECTION = [
    {'col': MONGO_COLLECTION_URL, 'unique': True, 'indexfield': "url"},
]

