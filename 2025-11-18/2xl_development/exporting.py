import csv
import logging
from pymongo import MongoClient
from settings import MONGO_COLLECTION_PRODUCT_DATA, FILE_NAME, FILE_HEADERS, MONGO_DB

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Export:
    """Export product data from MongoDB to CSV with cleaning"""

    def __init__(self, writer):
        self.writer = writer
        # Connect to MongoDB
        self.mongo = MongoClient("mongodb://localhost:27017/")[MONGO_DB]

    def start(self):
        """Export as CSV file"""

        # Write headers first
        self.writer.writerow(FILE_HEADERS)
        logging.info(f"CSV Headers: {FILE_HEADERS}")

        # Iterate over product data
        for item in self.mongo[MONGO_COLLECTION_PRODUCT_DATA].find(no_cursor_timeout=True):
            product_id = item.get("product_id", "").strip()

            # Clean: Skip / delete items without product_id
            if not product_id:
                logging.info(f"Skipping & deleting URL without product_id: {item.get('url')}")
                self.mongo[MONGO_COLLECTION_PRODUCT_DATA].delete_one({"_id": item["_id"]})
                continue

            # Extract fields safely
            url = item.get("url", "")
            product_name = item.get("product_name", "")
            product_type = item.get("product_type", "")
            price = item.get("price", "")
            wasprice = item.get("wasPrice", "")
            discount = item.get("discount", "")
            stock = item.get("stock", "")
            quantity = item.get("quantity", "")
            details_string = item.get("details_string", "")
            product_color = item.get("product_color", "")
            material = item.get("material", "")
            breadcrumb = " > ".join(item.get("breadcrumb", []))
            specification = str(item.get("specification", {}))
            images = ",".join(item.get("image", []))

            # Prepare CSV row in same order as FILE_HEADERS
            row = [
                url,
                product_id,
                product_name,
                product_color,
                material,
                quantity,
                details_string,
                specification,
                product_type,
                price,
                wasprice,
                breadcrumb,
                stock,
                images,
                discount,
            ]

            self.writer.writerow(row)


if __name__ == "__main__":
    with open(FILE_NAME, "w", encoding="utf-8", newline="") as file:
        writer_file = csv.writer(file, delimiter=",", quotechar='"')
        export = Export(writer_file)
        export.start()
        logging.info(f"Export finished: {FILE_NAME}")
