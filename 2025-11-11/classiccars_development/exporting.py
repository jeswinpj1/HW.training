import csv
import re
import logging
from pymongo import MongoClient
from settings import MONGO_COLLECTION_DATA, MONGO_DB_NAME, MONGO_URI, FILE_NAME, FILE_HEADERS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")


class Export:
    """Export ClassicCars data to CSV"""

    def __init__(self, writer):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
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
        """Export as CSV file"""
        # Write headers
        self.writer.writerow(FILE_HEADERS)
        logging.info(f"CSV Headers: {FILE_HEADERS}")

        for item in self.db[MONGO_COLLECTION_DATA].find(no_cursor_timeout=True):
            # Extract fields with defaults
            source_link = self.clean_text(item.get("source_url", ""))
            make = self.clean_text(item.get("make", ""))
            model = self.clean_text(item.get("model", ""))
            year = self.clean_text(item.get("year", ""))
            VIN = self.clean_text(item.get("VIN", ""))
            price = self.clean_text(item.get("price", ""))
            mileage = self.clean_text(item.get("mileage", ""))
            transmission = self.clean_text(item.get("transmission", ""))
            engine = self.clean_text(item.get("engine", ""))
            color = self.clean_text(item.get("color", ""))
            fuel_type = self.clean_text(item.get("fuel_type", ""))
            body_style = self.clean_text(item.get("body_style", ""))
            # Fetch description
            description = item.get("description", "")
            # Remove unwanted phrases
            for phrase in ["Vehicle Description", "Read more"]:
                description = description.replace(phrase, "")
            # Strip extra whitespace
            description = description.strip()

            # Convert image_urls to comma-separated string
            image_urls = "" 
            for url in item.get("image_urls", []):
                if isinstance(url, str) and url.strip():
                    image_urls += url.strip() + ","
            image_urls = image_urls.rstrip(",")  # remove trailing comma

            row = [
                source_link,
                make,
                model,
                year,
                VIN,
                price,
                mileage,
                transmission,
                engine,
                color,
                fuel_type,
                body_style,
                description,
                image_urls,
            ]

            self.writer.writerow(row)

        logging.info("CSV export completed.")


if __name__ == "__main__":
    with open(FILE_NAME, "w", encoding="utf-8", newline="") as file:
        writer_file = csv.writer(file, delimiter=",", quotechar='"')
        exporter = Export(writer_file)
        exporter.start()
