
import json
import csv
from pymongo import MongoClient
from settings import MONGO_URI, DB_NAME, TARGET_COLLECTION

def export_to_json(output="wasalt_properties.json"):
    client = MongoClient(MONGO_URI)
    data = list(client[DB_NAME][TARGET_COLLECTION].find({}, {"_id": 0}))
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f" Exported {len(data)} records to {output}")
def export_to_csv(output="wasalt_properties.csv"):
    client = MongoClient(MONGO_URI)
    data = list(client[DB_NAME][TARGET_COLLECTION].find({}, {"_id": 0}))

    if not data:
        print("⚠ No data found in collection.")
        return

    # Extract all unique keys from documents to ensure all columns are exported
    fieldnames = sorted({key for doc in data for key in doc.keys()})

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f" Exported {len(data)} records to {output}")

if __name__ == "__main__":
    export_to_json()
    export_to_csv()
