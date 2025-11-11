import csv
import logging
import re
from pymongo import MongoClient
from settings import (
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_DATA,
    file_name,
    FILE_HEADERS,
)


class Export:
    """Post-Processing Export Script for Fastenal Data"""

    def __init__(self, writer):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.collection = self.db[MONGO_COLLECTION_DATA]
        self.writer = writer

    def clean_text(self, value):
        """Clean unwanted tags, whitespace, and commas."""
        if not value:
            return ""
        value = re.sub(r"<.*?>", "", str(value))  # remove HTML tags
        value = re.sub(r"\s+", " ", value).strip()  # collapse multiple spaces/newlines
        value = value.replace(",", " ")  # replace commas to protect CSV format
        return value

    def start(self):
        """Export MongoDB data as cleaned CSV"""
        logging.info("Starting Fastenal data export...")
        self.writer.writerow(FILE_HEADERS)
        logging.info(f"Header written with {len(FILE_HEADERS)} fields.")

        cursor = self.collection.find(no_cursor_timeout=True)

        for item in cursor:
            # Match your actual MongoDB field names
            product_category = self.clean_text(item.get("product_category"))
            sku = self.clean_text(item.get("sku"))
            company_name = self.clean_text(item.get("company_name"))
            manufacturer_name = self.clean_text(item.get("manufacturer_name"))
            brand_name = self.clean_text(item.get("brand_name"))
            vendor_seller_part_number = self.clean_text(item.get("vendor_seller_part_number") or sku)
            item_name = self.clean_text(item.get("item_name"))
            full_product_description = self.clean_text(item.get("full_product_description"))
            price = self.clean_text(item.get("price"))
            unit_of_issue = self.clean_text(item.get("unit_of_issue"))
            qty_per_uoi = self.clean_text(item.get("qty_per_uoi"))
            availability = self.clean_text(item.get("availability"))
            manufacturer_part_number = self.clean_text(item.get("manufacturer_part_number"))
            country_of_origin = self.clean_text(item.get("country_of_origin") or "")
            upc = self.clean_text(item.get(" "))
            model_number = self.clean_text(item.get("model_number") or "")
            url = self.clean_text(item.get("url"))

            # --- CSV row ---
            data = [
                product_category,
                sku,
                company_name,
                manufacturer_name,
                brand_name,
                vendor_seller_part_number,
                item_name,
                full_product_description,
                price,
                unit_of_issue,
                qty_per_uoi,
                availability,
                manufacturer_part_number,
                country_of_origin,
                upc,
                model_number,
                url,
            ]

            self.writer.writerow(data)

        cursor.close()
        self.client.close()
        logging.info("Export completed successfully!")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s: %(message)s",
    )

    with open(file_name, "w", encoding="utf-8", newline="") as file:
        writer_file = csv.writer(file, delimiter=",", quotechar='"')
        export = Export(writer_file)
        export.start()
