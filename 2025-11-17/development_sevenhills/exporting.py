import csv
import logging
from pymongo import MongoClient
from settings import FILE_HEADERS, FILE_NAME, MONGO_URI, MONGO_DB

class Export:
    def __init__(self, writer):
        self.writer = writer
        client = MongoClient(MONGO_URI)

        # Export from DB used during scraping
        self.db = client[MONGO_DB]

        # Auto-detect correct collection name
        if "product_item" in self.db.list_collection_names():
            self.collection = "product_item"
        else:
            self.collection = "sevenhills_data"

        print("Using DB:", MONGO_DB)
        print("Using Collection:", self.collection)
        print("Count:", self.db[self.collection].count_documents({}))

    def start(self):
        self.writer.writerow(FILE_HEADERS)
        logging.info("CSV Headers Written")

        cursor = self.db[self.collection].find({})

        for item in cursor:
            data = [
                item.get("url", ""),
                item.get("make", ""),
                item.get("model", ""),
                item.get("year", ""),
                item.get("vin", ""),
                item.get("stock_no", ""),
                item.get("price", ""),
                item.get("mileage", ""),
                item.get("transmission", ""),
                item.get("engine", ""),
                item.get("exterior_color", ""),
                item.get("interior_color", ""),
                item.get("body_style", ""),
                item.get("description", ""),
                ",".join(item.get("image_urls", [])),
            ]

            self.writer.writerow(data)

        cursor.close()


if __name__ == "__main__":
    with open(FILE_NAME, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        export = Export(writer)
        export.start()
