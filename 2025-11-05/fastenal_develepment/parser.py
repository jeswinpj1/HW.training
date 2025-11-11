import time
import logging
import requests
from pymongo import MongoClient
from mongoengine import connect
from item import ProductItem  # MongoEngine schema
from settings import headers, cookies, API_URL, MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_DATA
SOURCE_COLLECTION = "pdp_urls_and_data"
DEST_COLLECTION = MONGO_COLLECTION_DATA
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")
client = MongoClient(MONGO_URI)
source_col = client[MONGO_DB_NAME][SOURCE_COLLECTION]
dest_col = client[MONGO_DB_NAME][DEST_COLLECTION]
# MongoEngine connection for ProductItem
connect(
    db=MONGO_DB_NAME,
    host=MONGO_URI
)
session = requests.Session()
# --- Get all products ---
products = list(source_col.find({}))
logging.info(f"Total SKUs to process: {len(products)}")
for product in products[:1000]:  # limit for testing
    sku = product.get("sku")
    if not sku:
        continue
    # --- Get product detail from API ---
    payload = {
        "sku": [sku],
        "productDetails": True,
        "attributeFilters": {},
        "pageUrl": f"/product/details/{sku}"
    }
    response = session.post(API_URL, headers=headers, cookies=cookies, json=payload)
    if response.status_code != 200:
        logging.info(f"Skipped SKU {sku}, status code {response.status_code}")
        continue
    api_details = response.json().get("productDetail", {})
    final_product = dict(product)
    # --- Fill missing fields from API ---
    final_product["Full Product Description"] = final_product.get("Full Product Description") or api_details.get("notes", {}).get("mp_bulletPoints", "")
    final_product["unspscCode"] = final_product.get("unspscCode") or api_details.get("unspscCode", "")
    final_product["Model Number"] = final_product.get("Model Number") or api_details.get("modelNumber", "")
    final_product["Manufacturer Part Number"] = final_product.get("Manufacturer Part Number") or api_details.get("manufacturerPartNumber", "")
    if not final_product.get("URL") and final_product.get("pdp_url"):
        final_product["URL"] = final_product["pdp_url"]
    # --- Split Unit of Issue ---
    unit = final_product.get("Unit of Issue", "")
    qty = ""
    if " of " in unit:
        unit_parts = unit.split(" of ")
        final_product["Unit of Issue"] = unit_parts[0]
        qty = unit_parts[1]
    final_product["QTY Per UOI"] = qty
    # --- Build ProductItem object ---
    product_obj = ProductItem(
        sku=sku,
        company_name=final_product.get("Company Name", ""),
        manufacturer_name=final_product.get("Manufacturer Name", ""),
        brand_name=final_product.get("Brand Name", ""),
        vendor_seller_part_number=final_product.get("sku", ""),
        item_name=final_product.get("Item Name", ""),
        full_product_description=final_product.get("Full Product Description", ""),
        price=final_product.get("Price", ""),
        unit_of_issue=final_product.get("Unit of Issue", ""),
        qty_per_uoi=final_product.get("QTY Per UOI", ""),
        product_category=final_product.get("categoryLevelOne", ""),
        url=final_product.get("URL", ""),
        availability=final_product.get("Availability", ""),
        manufacturer_part_number=final_product.get("Manufacturer Part Number", ""),
        country_of_origin=final_product.get("Country of Origin", ""),
        upc=final_product.get("UPC", ""),
        model_number=final_product.get("Model Number", "")
    )
    # --- Save ProductItem using MongoEngine ---
    product_obj.save()
    # --- Also save to final_data collection using PyMongo ---
    dest_col.update_one({"sku": sku}, {"$set": product_obj.to_mongo().to_dict()}, upsert=True)
    logging.info(f"Processed and saved SKU: {sku}")
    time.sleep(0.5)
client.close()
logging.info(f" All products updated and saved to '{DEST_COLLECTION}'")

