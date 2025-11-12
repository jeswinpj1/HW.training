from datetime import datetime
import calendar
import logging
import pytz
import requests

# -------------------------
# Logging Configuration
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# -------------------------
# Basic Project Details
# -------------------------
PROJECT = "classiccars_crawler"
CLIENT_NAME = "ClassicCars"
PROJECT_NAME = "classiccars"
FREQUENCY = "daily"
BASE_URL = "https://classiccars.com/listings/find/until-1990"

# -------------------------
# Date & File Naming
# -------------------------
datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))

iteration = datetime_obj.strftime("%Y_%m_%d")
YEAR = datetime_obj.strftime("%Y")
MONTH = datetime_obj.strftime("%m")
DAY = datetime_obj.strftime("%d")
MONTH_VALUE = calendar.month_abbr[int(MONTH.lstrip("0"))]
WEEK = (int(DAY) - 1) // 7 + 1

FILE_NAME = f"1classiccars_1{iteration}.csv"

# -------------------------
# MongoDB Settings
# -------------------------
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = f"classiccars_{iteration}"
MONGO_COLLECTION_URLS = f"{PROJECT_NAME}_urls"
MONGO_COLLECTION_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_data"

# -------------------------
# Headers & Requests Config
# -------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.classiccars.com/",
    "Connection": "keep-alive"
}

COOKIES = {
    "IDE": "AHWqTUkOeRTNh07YhdhUD176dl3is_181CUVbLfHUzDhrBJt7Oj6pRD_hha5KKGkPu4",
    "DSID": "AEhM4MfwkxlssRFoHWRFN-HIBBA0Wkv21MqEMJpvO5mjya5kQgqh-mwVXswfNp_mDP-PPAxaeXf2Cz6VCB9lYuu63G8n82egqk3KiKNHSUF3P50Ru_PyoJfjlqKvOrKy8MHrxOHxkDrxnMRMtGTTdgc0NwGGigl0mceTqcbl47u8FfIsyI1zCjQ9Tt_sB6JVilPfJ1xyXgJygkl7eNamD8IaJthw2YZj4l_T-0NMLJdWedMDsqcCkvrXzJY4K7rQn9Y5N1MKRjjJJkeRDCoh6m7uKLGAa4FyzzTANStQDnJ7i_1y8TbR4TY"
}
FILE_HEADERS = [
    "source_link", "make", "model", "year", "VIN", "price", "mileage",
    "transmission", "engine", "color", "fuel_type", "body_style",
    "description", "image_urls"
]
