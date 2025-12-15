from datetime import datetime
import calendar
import logging
import pytz
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# basic details
PROJECT = "PHARMAMARKET"
CLIENT_NAME = ""
PROJECT_NAME = "pharmamarket_scraper"
FREQUENCY = "ONETIME"
BASE_URL = "https://www.pharmamarket.be/"


datetime_obj = datetime.now(pytz.timezone("Asia/Kolkata"))

iteration = datetime_obj.strftime("%Y_%m_%d")
YEAR = datetime_obj.strftime("%Y")
MONTH = datetime_obj.strftime("%m")
DAY = datetime_obj.strftime("%d")
MONTH_VALUE = calendar.month_abbr[int(MONTH.lstrip("0"))]
WEEK = (int(DAY) - 1) // 7 + 1

FILE_NAME = f"pharmamarket_{iteration}"

# Mongo db and collections - Adjusted to your specific names
MONGO_DB = "pharmamarket_db" 
MONGO_COLLECTION_INPUT = "input_data"
MONGO_COLLECTION_DATA = f"{PROJECT_NAME}_url"
MONGO_COLLECTION_DETAILS = f"{PROJECT_NAME}_data"
MONGO_COLLECTION_URL_FAILED = f"{PROJECT_NAME}_url_failed"
MONGO_COL_URL = f"{PROJECT_NAME}_url"


# Headers and useragents and other variables
SHARD_COLLECTION = [
    {'col': MONGO_COL_URL, 'unique': True, 'indexfield': "url"}, 
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


client = MongoClient("mongodb://localhost:27017/")
db = client[MONGO_DB]
input_col = db[MONGO_COLLECTION_INPUT] 
output_col = db[MONGO_COLLECTION_DATA]
