import requests
import json
from urllib.parse import quote
import time

# --- Session & Headers ---
session = requests.Session()
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "fastnel" 
MONGO_COLLECTION_CATEGORY = "catogary_id_extraction" 
MONGO_COLLECTION_PRODUCTS = "pdp_urls_and_data"
MONGO_COLLECTION_DATA = "final_data"
file_name = "DataHut_USA_Fastenal_FullDump_20251111.CSV"

FILE_HEADERS = [
                "product_category",
                "sku",
                "company_name",
                "manufacturer_name",
                "brand_name",
                "vendor_seller_part_number",
                "item_name",
                "full_product_description",
                "price",
                "unit_of_issue",
                "qty_per_uoi",
                "availability",
                "manufacturer_part_number",
                "country_of_origin",
                "upc",
                "model_number",
                "url",
            ]
headers = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "referer": "https://www.fastenal.com/product/all",
    "origin": "https://www.fastenal.com",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "x-xsrf-token": "YOUR_XSRF_TOKEN_HERE",  # replace
}

cookies = {
    "XSRF-TOKEN": "YOUR_XSRF_TOKEN_HERE",
    "CJSESSIONID": "YOUR_SESSION_ID",
    "TSESSIONID": "YOUR_TSESSION_ID",
}

category_menu_url = "https://www.fastenal.com/container/api/product-search/category-menu"
product_search_url = "https://www.fastenal.com/catalog/api/product-search"
API_URL = "https://www.fastenal.com/catalog/api/product-search"
