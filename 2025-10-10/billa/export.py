import csv
import logging
import re
from pymongo import MongoClient
from settings import FILE_NAME_FULLDUMP, CSV_DELIMITER, CSV_QUOTECHAR, MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_ENRICHED_DATA

logging.basicConfig(level=logging.INFO)
mongo_client = MongoClient(MONGO_URI)
col_enriched = mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_ENRICHED_DATA]

# Fields must match the 126 header format
CSV_HEADERS = [
    "unique_id","competitor_name","store_name","store_addressline1","store_addressline2","store_suburb",
    "store_state","store_postcode","store_addressid","extraction_date","product_name","brand","brand_type",
    "grammage_quantity","grammage_unit","drained_weight","producthierarchy_level1","producthierarchy_level2",
    "producthierarchy_level3","producthierarchy_level4","producthierarchy_level5","producthierarchy_level6",
    "producthierarchy_level7","regular_price","selling_price","price_was","promotion_price","promotion_valid_from",
    "promotion_valid_upto","promotion_type","percentage_discount","promotion_description","package_sizeof_sellingprice",
    "per_unit_sizedescription","price_valid_from","price_per_unit","multi_buy_item_count","multi_buy_items_price_total",
    "currency","breadcrumb","pdp_url","variants","product_description","instructions","storage_instructions",
    "preparationinstructions","instructionforuse","country_of_origin","allergens","age_of_the_product","age_recommendations",
    "flavour","nutritions","nutritional_information","vitamins","labelling","grade","region","packaging","receipies",
    "processed_food","barcode","frozen","chilled","organictype","cooking_part","handmade","max_heating_temperature",
    "special_information","label_information","dimensions","special_nutrition_purpose","feeding_recommendation","warranty",
    "color","model_number","material","usp","dosage_recommendation","tasting_note","food_preservation","size","rating",
    "review","file_name_1","image_url_1","file_name_2","image_url_2","file_name_3","image_url_3","competitor_product_key",
    "fit_guide","occasion","material_composition","style","care_instructions","heel_type","heel_height","upc","features",
    "dietary_lifestyle","manufacturer_address","importer_address","distributor_address","vinification_details","recycling_information",
    "return_address","alchol_by_volume","beer_deg","netcontent","netweight","site_shown_uom","ingredients","random_weight_flag",
    "instock","promo_limit","product_unique_key","multibuy_items_pricesingle","perfect_match","servings_per_pack","warning",
    "suitable_for","standard_drinks","environmental","grape_variety","retail_limit"
]


def clean_value(value):
    """Cleans each value before writing."""
    if value is None:
        return ""

    # Convert to string
    value = str(value)

    # Remove HTML tags
    value = re.sub(r'<.*?>', ' ', value)

    # Remove unwanted symbols (optional: keep basic punctuation)
    value = re.sub(r'[^\w\s\.,:/%-]', ' ', value)

    # Convert boolean-like fields
    if value.strip().lower() == "true":
        return True
    if value.strip().lower() == "false":
        return False

    # Remove extra whitespace and convert to lowercase
    return re.sub(r'\s+', ' ', value).strip().lower()


class Export:
    def __init__(self, out_path=FILE_NAME_FULLDUMP):
        self.out_path = out_path
        self.col = col_enriched

    def start(self):
        with open(self.out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(CSV_HEADERS)

            for doc in self.col.find({}):
                row = [clean_value(doc.get(h, "")) for h in CSV_HEADERS]
                writer.writerow(row)
                logging.info("Wrote: %s (%s)", doc.get("product_name", "")[:50], doc.get("unique_id", ""))


if __name__ == "__main__":
    Export().start()
