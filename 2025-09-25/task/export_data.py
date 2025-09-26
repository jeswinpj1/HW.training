
import csv
import json
import logging
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "interspar"
PRODUCT_COLLECTION = "products"

FIELDS_FILE = "fields_126.json"
OUTPUT_FILE = "interspar_products.csv"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
col = db[PRODUCT_COLLECTION]

with open(FIELDS_FILE, "r", encoding="utf-8") as f:
    FIELDS = json.load(f)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter="|")
    writer.writeheader()
    for doc in col.find():
        row = {field: doc.get(field, "") for field in FIELDS}
        writer.writerow(row)

logging.info(f"Exported {col.count_documents({})} docs to {OUTPUT_FILE}")