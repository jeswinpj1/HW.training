# import logging
# from datetime import datetime
# import calendar
# import pytz

# # ----------------- Logging -----------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(levelname)s:%(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )

# # ----------------- Project Info -----------------
# PROJECT       = "site_lidl"
# PROJECT_NAME  = "LIDL"
# CLIENT_NAME   = "LIDL"        # if needed for export consistency
# FREQUENCY     = "POC"
# BASE_URL      = "https://www.lidl.co.uk"
# REQUEST_DELAY = 0.5           # optional – useful to slow API traffic

# # ----------------- Extraction Date -----------------
# datetime_obj      = datetime.now(pytz.timezone("Asia/Kolkata"))
# EXTRACTION_DATE   = datetime_obj.strftime("%Y-%m-%d")    # YYYY-MM-DD
# iteration         = datetime_obj.strftime("%Y_%m_%d")
# YEAR              = datetime_obj.strftime("%Y")
# MONTH             = datetime_obj.strftime("%m")
# DAY               = datetime_obj.strftime("%d")
# MONTH_VALUE       = calendar.month_abbr[int(MONTH.lstrip("0"))]
# WEEK              = (int(DAY) - 1) // 7 + 1

# # ----------------- Output File Name -----------------
# FILE_NAME_FULLDUMP = f"_lidldata_{datetime_obj:%Y%m%d}.CSV"

# # ----------------- MongoDB -----------------
# MONGO_URI                       = "mongodb://localhost:27017/"
# MONGO_DB                        = f"lidl(1)_2025_10_27{iteration}"
# MONGO_COLLECTION_DATA           = f"{PROJECT_NAME}_data"
# MONGO_COLLECTION_ENRICHED_DATA  = f"{PROJECT_NAME}_full126_data"       # matches old logic
# MONGO_COLLECTION_URL_FAILED     = f"{PROJECT_NAME}_url_failed"
# MONGO_COLLECTION_CATEGORY        = f"{PROJECT_NAME}_category_url"       # optional if needed

# # ----------------- API -----------------
# API_URL = (
#     "https://www.lidl.co.uk/q/api/search?"
#     "offset=12&fetchsize=12&locale=en_GB&assortment=GB&version=2.1.0&category.id="
# )

# # ----------------- Headers -----------------
# HEADERS = {
#     "Accept": "application/mindshift.search+json;version=2",
#     "Accept-Language": "en-US,en;q=0.9",
#     "User-Agent": (
#         "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) "
#         "Gecko/20100101 Firefox/115.0"
#     ),
#     "Referer": "https://www.lidl.co.uk/",
# }

# # ----------------- CSV -----------------
# CSV_DELIMITER = "|"
# CSV_QUOTECHAR = '"'

# # ----------------- Grammage (Qty + Unit extraction) -----------------
# GRAMMAGE_REGEX = (
#     r'(\d+(?:[.,]\d+)?)(?:\s?x\s?\d+(?:[.,]\d+)?)?\s?'
#     r'(ml|l|g|kg|cl|dl|oz|lt|pcs|st|stück)\b'
# )


#..............................................................................................................................................


# settings.py
import logging
from datetime import datetime
import calendar
import pytz
from mongoengine import connect, errors

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

PROJECT       = "site_lidl"
PROJECT_NAME  = "LIDL"
CLIENT_NAME   = "LIDL"
FREQUENCY     = "POC"
BASE_URL      = "https://www.lidl.co.uk"

# Extraction Date
datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))
EXTRACTION_DATE = datetime_obj.strftime("%Y-%m-%d")


FILE_NAME_FULLDUMP = f"DataHut_UK_Lidl_FullDump_{datetime_obj:%Y%m%d}.CSV"

# MONGO SETTINGS  FIXED
MONGO_URI  = "mongodb://localhost:27017/"
MONGO_DB   = f"lidl(1)_2025_10_27"    
MONGO_COLLECTION_DATA = "LIDL_data"
MONGO_COLLECTION_ENRICHED_DATA = "lidl_full126"
MONGO_COLLECTION_URL_FAILED = "lidl_url_failed"

# API
API_URL = (
    "https://www.lidl.co.uk/q/api/search?"
    "offset=12&fetchsize=12&locale=en_GB&assortment=GB&version=2.1.0&category.id="
)

HEADERS = {
    "Accept": "application/mindshift.search+json;version=2",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Referer": "https://www.lidl.co.uk/",
}

CSV_DELIMITER = "|"
CSV_QUOTECHAR = '"'
