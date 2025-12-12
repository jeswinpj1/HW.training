import logging
import re
from pymongo import MongoClient
from settings import FILE_NAME, MONGO_URI, MONGO_DB


logging.basicConfig(level=logging.INFO)

# --- 126 Fields ---
FIELDS_126 = [
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


# Mongo connection
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db["lidl_products"]

def clean_value(value):
    """Clean text and remove HTML and extra spaces."""
    if value is None:
        return ""
    value = str(value)
    value = re.sub(r'</?(li|div|ul|ol|br|p|strong)[^>]*>', ' ', value, flags=re.IGNORECASE)
    value = re.sub(r'\s+', ' ', value).strip()
    value = value.replace("|", " ")  # avoid breaking delimiter
    return value

class ExportPipe:
    def __init__(self, out_path=FILE_NAME):
        self.out_path = out_path

    def start(self):
        with open(self.out_path, "w", encoding="utf-8") as f:
            # Write header
            f.write("|".join(FIELDS_126) + "\n")
            


            for doc in collection.find({}):
                export_doc = {}

                for field in FIELDS_126:
                    # skip levels because we already set them
                    # if field.startswith("producthierarchy_level"):
                    #     continue

                    value = doc.get(field, "")
                    if isinstance(value, str) or value is None:
                        value = clean_value(value)
                    else:
                        value = str(value)  # convert numbers/booleans to string

                    export_doc[field] = value

                # Ensure all fields are in order of FIELDS_126
                row = [export_doc.get(f, "") for f in FIELDS_126]
                f.write("|".join(row) + "\n")
                logging.info("Wrote: %s (%s)", doc.get("product_name", "")[:50], doc.get("unique_id", ""))

if __name__ == "__main__":
    ExportPipe().start()
