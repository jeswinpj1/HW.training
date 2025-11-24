import requests
import logging
from lxml import html
from mongoengine import connect, Document, StringField
from settings import PROJECT_NAME, iteration,HEADERS,BASE_URL
from item import SubcategoryItem

# --------------------------------------------------------
# --- Configuration (Based on typical project settings) ---
# Replace with your actual configuration from settings.py
# Assuming these are available in your environment or project setup
MONGO_DB = f"{PROJECT_NAME}_{iteration}"
BASE_URL = BASE_URL
HEADERS = HEADERS
# --------------------------------------------------------

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 1. Define the MongoEngine Model ---


# --- 2. Define the Extractor Class ---
class SubcategoryExtractor:
    def __init__(self):
        # Connect to MongoDB
        logging.info(f"Connecting to MongoDB: {MONGO_DB}")
        connect(db=MONGO_DB, host="localhost", alias="default")
        self.db_connection = True

    def _extract_subcategories(self):
        """Extract Subcategories (simple, no try/except) - Helper method for start()"""

        logging.info("Extracting subcategories…")
        resp = requests.get(BASE_URL, headers=HEADERS)
        tree = html.fromstring(resp.content)
        li_elements = tree.xpath("//li[@data-subcat-id]")

        subcats = []
        for li in li_elements:
            subcat_id = li.get("data-subcat-id")
            a = li.find(".//a")
            subcat_name = a.text_content().strip() if a is not None else ""

            subcats.append({
                "subcat_id": subcat_id,
                "text": subcat_name
            })

        logging.info(f"Found {len(subcats)} subcategories")
        return subcats

    def run_and_save(self):
        """
        Executes the extraction and saves the results to the database.
        """
        subcategories = self._extract_subcategories()
        
        logging.info(f"Starting database save for {len(subcategories)} items.")
        
        for subcat in subcategories:
            try:
                # Create a new SubcategoryItem instance
                item = SubcategoryItem(
                    subcat_id=subcat["subcat_id"],
                    name=subcat["text"]
                )
                # Save the item to the 'subcategories' collection
                item.save()
                logging.info(f"Saved: ID={subcat['subcat_id']}, Name='{subcat['text']}'")
            except Exception as e:
                # Log a warning if the item is a duplicate or another error occurs
                if "E11000 duplicate key error" in str(e):
                    logging.warning(f"Skipped duplicate ID: {subcat['subcat_id']}")
                else:
                    logging.error(f"Error saving ID {subcat['subcat_id']}: {e}")

# --- 3. Main Runner ---
if __name__ == "__main__":
    extractor = SubcategoryExtractor()
    extractor.run_and_save()