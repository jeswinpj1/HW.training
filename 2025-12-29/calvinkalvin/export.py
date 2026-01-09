import csv
from pymongo import MongoClient

# ---------------- MongoDB Setup ----------------
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "calvinklein"
COLLECTION_NAME = "product_crawl_data"
OUTPUT_FILE = "calvinklein_2025-12-29_sample.csv"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ---------------- CSV Headers ----------------
csv_headers = [
    "url",
    "product_sku",
    "product_name",
    "brand",
    "currency",
    "original_price",
    "sale_price",
    "category",
    "total_number_of_reviews",
    "rating",
    "description",
    "features",
    "color",
    "size"
]

# ---------------- Fetch Data ----------------
all_products = collection.find()

# ---------------- Write CSV ----------------
with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
    writer.writeheader()

    for product in all_products:
        # Flatten lists into comma-separated strings
        features = product.get("features", []) + product.get("table_features", [])
        features_str = ", ".join([f.replace(",", ";") for f in features])  # avoid breaking CSV

        color_str = ", ".join([c.replace(",", ";") for c in product.get("color", [])])
        size_str = ", ".join([s.replace(",", ";") for s in product.get("size", [])])

        row = {
            "url": product.get("url", ""),
            "product_sku": product.get("product_sku", ""),
            "product_name": product.get("product_name", ""),
            "brand": product.get("brand", ""),
            "currency": product.get("currency", ""),
            "original_price": product.get("original_price", ""),
            "sale_price": product.get("sale_price", ""),
            "category": product.get("category", ""),
            "total_number_of_reviews": product.get("total_number_of_reviews", 0),
            "rating": product.get("rating", 0),
            "description": product.get("description", "").replace("\n", " ").replace("\r", " "),
            "features": features_str,
            "color": color_str,
            "size": size_str
        }

        writer.writerow(row)

print(f"Export completed: {OUTPUT_FILE}")
client.close()
