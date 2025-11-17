import csv
import logging
import re
from html import unescape
from settings import (client, collection_products, file_name, FILE_HEADERS)

class Export:
    """Export parsed product data into CSV"""

    def __init__(self, writer):
        self.mongo = client
        self.writer = writer

    def clean(self, value):
        """Convert None, lists, HTML and unwanted values into clean CSV text."""

        if value is None:
            return ""

        # If list -> join values
        if isinstance(value, list):
            value = ",".join([str(v).strip() for v in value if v])

        value = str(value).strip()

        # Inline clean (HTML decode + remove tags)
        value = unescape(value)  # decode HTML entities
        value = re.sub(r"<[^>]+>", " ", value)  # strip tags
        value = " ".join(value.split())  # remove extra spaces

        return value

    def start(self):
        """Export MongoDB product collection into CSV"""

        # Write headers
        self.writer.writerow(FILE_HEADERS)
        logging.info("CSV Headers Written")

        # Fetch all product documents
        for item in collection_products.find(no_cursor_timeout=True):

            data = [
                self.clean(item.get("retailer_id")),
                self.clean(item.get("retailer")),
                self.clean(item.get("product_name")),
                self.clean(item.get("brand")),
                self.clean(item.get("grammage_quantity")),
                self.clean(item.get("grammage_unit")),
                self.clean(item.get("original_price")),
                self.clean(item.get("selling_price")),
                self.clean(item.get("promotion_description")),
                self.clean(item.get("pdp_url")),
                self.clean(item.get("image_url")),
                self.clean(item.get("ingredients")),
                self.clean(item.get("directions")),
                self.clean(item.get("disclaimer")),
                self.clean(item.get("description")),
                self.clean(item.get("diet_suitability")),
                self.clean(item.get("colour")),
                self.clean(item.get("hair_type")),
                self.clean(item.get("skin_type")),
                self.clean(item.get("skin_tone")),
            ]

            self.writer.writerow(data)

        logging.info("CSV Export Completed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with open(file_name, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"')
        export = Export(writer)
        export.start()

    logging.info("File Saved → " + file_name)