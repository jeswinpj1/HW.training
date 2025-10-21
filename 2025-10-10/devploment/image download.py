#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download images for Billa products from MongoDB
-----------------------------------------------
- Reads all products from MongoDB collection
- Downloads image_url_1, image_url_2, image_url_3 (if available)
- Saves them as file_name_1, file_name_2, file_name_3 in ./billa_images/
"""

import os
import time
import requests
from pymongo import MongoClient

# ---------------- CONFIG ----------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "billa_scraper12"
COLLECTION = "product_data"

IMAGE_DIR = "billa_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}
REQUEST_DELAY = 0.8

# ---------------- MONGO ----------------
mongo_client = MongoClient(MONGO_URI)
col = mongo_client[DB_NAME][COLLECTION]

# ---------------- IMAGE DOWNLOAD FUNCTION ----------------
def download_image(image_url, file_name):
    if not image_url or not file_name:
        return False
    img_path = os.path.join(IMAGE_DIR, file_name)
    if os.path.exists(img_path):
        print(f"Already exists: {file_name}")
        return True
    try:
        res = requests.get(image_url, headers=HEADERS, timeout=25)
        if res.status_code == 200:
            with open(img_path, "wb") as f:
                f.write(res.content)
            print(f"Saved: {file_name}")
            return True
        else:
            print(f"Failed ({res.status_code}): {image_url}")
            return False
    except Exception as e:
        print(f"Error downloading {image_url}: {e}")
        return False

# ---------------- MAIN LOOP ----------------
all_products = list(col.find({}, {"unique_id": 1, "image_url_1": 1, "file_name_1": 1,
                                  "image_url_2": 1, "file_name_2": 1,
                                  "image_url_3": 1, "file_name_3": 1}))

print(f"Found {len(all_products)} products to process.")

for i, product in enumerate(all_products, 1):
    for n in range(1, 4):
        img_url = product.get(f"image_url_{n}", "")
        img_name = product.get(f"file_name_{n}", "")
        if img_url and img_name:
            download_image(img_url, img_name)
            time.sleep(REQUEST_DELAY)
    print(f"[{i}/{len(all_products)}] Done: {product.get('unique_id')}")

print("✅ Image download complete.")
