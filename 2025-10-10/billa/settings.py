# # # settings.py
# # from datetime import datetime
# # import logging
# # import pytz

# # logging.basicConfig(
# #     level=logging.INFO,
# #     format="%(asctime)s %(levelname)s:%(message)s",
# #     datefmt="%Y-%m-%d %H:%M:%S",
# # )

# # # Project
# # PROJECT = "billa_scraper"
# # CLIENT_NAME = "Billa"
# # PROJECT_NAME = "billa"
# # BASE_URL = "https://shop.billa.at/"
# # REQUEST_DELAY = 1.5
# # TOTAL_PAGES = 352
# # PAGE_SIZE = 30
# # STORE_ID = "00-10"

# # # Mongo
# # MONGO_URI = "mongodb://localhost:27017/"
# # MONGO_DB_NAME = "billa_scraper"

# # # Datetime / filenames
# # datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))
# # iteration = datetime_obj.strftime("%Y_%m_%d")
# # EXTRACTION_DATE = datetime_obj.strftime("%Y-%m-%d")
# # FILE_NAME_FULLDUMP = f"DataHut_Austria_Billa_FullDump_{datetime_obj:%Y%m%d}.CSV"

# # # Collections
# # MONGO_COLLECTION_DATA = "product_data"
# # MONGO_COLLECTION_ENRICHED_DATA = "full126_product_data"
# # MONGO_COLLECTION_URL_FAILED = "billa_url_failed"
# # MONGO_COLLECTION_CATEGORY = "billa_category_url"

# # # Headers
# # HEADERS_PAGE = {
# #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
# #                   "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
# # }

# # # Grammage regex (used by parser)
# # GRAMMAGE_REGEX = r'(\d+(?:[.,]\d+)?)(?:\s?x\s?\d+(?:[.,]\d+)?)?\s?(ml|l|g|kg|cl|dl|oz|lt|pcs|st|stück)\b'

# # # CSV
# # CSV_DELIMITER = "|"
# # CSV_QUOTECHAR = '"'



# #working^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# from datetime import datetime

# # Basic project info
# CLIENT_NAME = "Billa_test"
# STORE_ID = "00-10"
# REQUEST_DELAY = 0.5  # seconds between API requests

# # Extraction date
# EXTRACTION_DATE = datetime.now().strftime("%Y-%m-%d")

# # Headers for requests
# HEADERS_PAGE = {
#     "User-Agent": (
#         "Mozilla/5.0 (X11; Linux x86_64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/141.0.0.0 Safari/537.36"
#     ),
#     "Accept": "application/json"
# }

# # API endpoint
# API_URL = "https://shop.billa.at/api/product-discovery/products"

# # Regex for grammage
# GRAMMAGE_REGEX = r'(\d+(?:[.,]\d+)?)(?:\s?x\s?\d+(?:[.,]\d+)?)?\s?(ml|l|g|kg|cl|dl|oz|lt|pcs|st|stück)\b'



#...................................................................................................................................................


# settings.py
from datetime import datetime
import pytz
import logging

# ----------------- Logging -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ----------------- Project Info -----------------
PROJECT = "billa_scraper"
PROJECT_NAME = "billa"
CLIENT_NAME = "Billa"  # use "Billa_test" if testing
BASE_URL = "https://shop.billa.at/"
STORE_ID = "00-10"
REQUEST_DELAY = 0.5  # seconds between API requests
TOTAL_PAGES = 352
PAGE_SIZE = 30

# ----------------- Extraction Date -----------------
datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))
EXTRACTION_DATE = datetime_obj.strftime("%Y-%m-%d")
FILE_NAME_FULLDUMP = f"DataHut_Austria_Billa_FullDump_{datetime_obj:%Y%m%d}.CSV"

# ----------------- MongoDB -----------------
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "billa_scraper"
MONGO_COLLECTION_DATA = "product_data"
MONGO_COLLECTION_ENRICHED_DATA = "full126_product_data"
MONGO_COLLECTION_URL_FAILED = "billa_url_failed"
MONGO_COLLECTION_CATEGORY = "billa_category_url"

# ----------------- Headers -----------------
HEADERS_PAGE = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/141.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json"
}

# ----------------- API -----------------
API_URL = "https://shop.billa.at/api/product-discovery/products"

# ----------------- Grammage -----------------
GRAMMAGE_REGEX = r'(\d+(?:[.,]\d+)?)(?:\s?x\s?\d+(?:[.,]\d+)?)?\s?(ml|l|g|kg|cl|dl|oz|lt|pcs|st|stück)\b'

# ----------------- CSV -----------------
CSV_DELIMITER = "|"
CSV_QUOTECHAR = '"'
