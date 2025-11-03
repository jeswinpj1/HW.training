# ----------------- Imports -----------------
import logging
from datetime import datetime
import pytz

# ----------------- Logging -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ----------------- Project Info -----------------
PROJECT = "kulud_feasibility"
PROJECT_NAME = "kulud"
CLIENT_NAME = "Kulud"

BASE_URL = "https://kuludonline.com/collections"
REQUEST_DELAY = 1.0  # seconds between requests
REQUEST_TIMEOUT = 30  # seconds

# ----------------- Extraction Date -----------------
datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))
EXTRACTION_DATE = datetime_obj.strftime("%Y-%m-%d")
FILE_NAME_FULLDUMP = f"DataHut_Qatar_Kulud_FullDump_{datetime_obj:%Y%m%d}.CSV"

# ----------------- MongoDB -----------------
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "kulud_scraper"
MONGO_COLLECTION_CATEGORY = "kulud_category_data"
MONGO_COLLECTION_PRODUCT = "kulud_product_data"
MONGO_COLLECTION_FAILED_URLS = "kulud_failed_urls"

# ----------------- Headers -----------------
HEADERS_PAGE = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

# ----------------- CSV -----------------
CSV_DELIMITER = "|"
CSV_QUOTECHAR = '"'

# ----------------- Misc -----------------
RETRY_COUNT = 3  # number of retries before marking URL as failed
POLITE_DELAY = 1.5  # delay between requests
