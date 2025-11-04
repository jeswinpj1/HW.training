import csv
import time
import re
from pymongo import MongoClient
from urllib.parse import urlparse
from settings import MONGO_URI, MONGO_DB_NAME, FILE_NAME_FULLDUMP

CSV_HEADERS = [
    "url",
    "product_name",
    "mrp",
    "sale_price",
    "discount",
    "instock",
    "timestamp"
]


class KuludExport:
    """Export unique Kulud products to CSV (ignores duplicate URLs across collections)"""

    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db["kulud_product_details"]
        self.seen = set()

    def normalize_url(self, url: str):
        """Keep only the last part of the product URL"""
        try:
            path = urlparse(url).path
            return path.strip("/").split("/")[-1].lower()
        except Exception:
            return url.lower()

    def start(self):
        """Fetch data, remove duplicates, and export to CSV"""
        with open(FILE_NAME_FULLDUMP, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="|", quotechar='"')
            writer.writerow(CSV_HEADERS)

            count = 0
            skipped = 0

            for item in self.collection.find({}, {field: 1 for field in CSV_HEADERS}):
                name = item.get("product_name", "").strip().lower()
                url = item.get("url", "").strip()
                normalized_url = self.normalize_url(url)

                # Use product name + last slug part of URL for uniqueness
                key = (name, normalized_url)
                if key in self.seen:
                    skipped += 1
                    continue
                self.seen.add(key)

                discount = re.sub(r"\bUp to\b", "", item.get("discount", ""), flags=re.IGNORECASE).strip()

                row = [
                    url,
                    item.get("product_name", ""),
                    item.get("mrp", ""),
                    item.get("sale_price", ""),
                    discount,
                    item.get("instock", ""),
                    item.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
                ]
                writer.writerow(row)
                count += 1

            print(f" Export complete — {count} records written to {FILE_NAME_FULLDUMP}")
            print(f" Skipped {skipped} duplicate records")

    def close(self):
        """Close MongoDB connection"""
        self.client.close()


if __name__ == "__main__":
    exporter = KuludExport()
    exporter.start()
    exporter.close()
