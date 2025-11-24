# ----------------------------------------------------
# Imports
# ----------------------------------------------------
from datetime import datetime
import pytz
import calendar


# ----------------------------------------------------
# Project Details
# ----------------------------------------------------
PROJECT = "1TwoXLHome"
CLIENT_NAME = "2XL"
PROJECT_NAME = "two_xl"
FREQUENCY = "Daily"

BASE_URL = "https://2xlhome.com"
MONGO_URI = "mongodb://localhost:27017/"


# ----------------------------------------------------
# Timestamp / Iteration Info
# ----------------------------------------------------
datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))

iteration = datetime_obj.strftime("%Y_%m_%d")
YEAR = datetime_obj.strftime("%Y")
MONTH = datetime_obj.strftime("%m")
DAY = datetime_obj.strftime("%d")
MONTH_VALUE = calendar.month_abbr[int(MONTH.lstrip("0"))]
WEEK = (int(DAY) - 1) // 7 + 1

FILE_NAME = f"{PROJECT_NAME}_{iteration}.csv"


# ----------------------------------------------------
# MongoDB Collections
# ----------------------------------------------------
MONGO_DB = f"two_xl_2025_11_21"

# URLs collected during crawling
MONGO_COLLECTION_PRODUCT_URLS = f"{PROJECT_NAME}_product_urls"

# Categories & Subcategories
MONGO_COLLECTION_CATEGORIES = f"{PROJECT_NAME}_categories"
MONGO_COLLECTION_SUBCATEGORIES = f"{PROJECT_NAME}_subcategories"


# Failed URLs
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_failed_urls"


# Product Details for Final Output
MONGO_COLLECTION_PRODUCT_DATA = f"{PROJECT_NAME}_product_data"


# Raw HTML or API responses (optional/debugging)
MONGO_COLLECTION_RESPONSE = f"{PROJECT_NAME}_response"

# Pagination records
MONGO_COLLECTION_PAGINATION = f"{PROJECT_NAME}_pagination"

# ------------------------------------------------------
# HEADERS AND COOKIES
# ------------------------------------------------------
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "user-agent":
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
}

COOKIES = {
    "PHPSESSID": "7fc1779817d0b383b7cc5606712246d2",
    "form_key": "d34LJvkYZTYtL88X",
}

# ------------------------------------------------------
# API TEMPLATE
# ------------------------------------------------------
API_TEMPLATE = (
    "https://2xlhome.com/ae-en/{slug}?p={page}&p={page}"
    "&_category_id={subcat_id}"
    "&_core_filters=W10%3D"
    "&_sections=product_list"
    "&isPowerListingAjax=b6bdd9ecd08caf7084a957e7d3e2126b"
)
FILE_HEADERS = [
    "url",
    "product_id",
    "product_name",
    "product_color",
    "material",
    "quantity",
    "details_string",
    "specification",
    "product_type",
    "price",
    "wasPrice",
    "breadcrumb",
    "stock",
    "image",
    "discount",
]