from mongoengine import DynamicDocument, StringField, ListField, BooleanField, FloatField
from settings import MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL, MONGO_COLLECTION_URL_FAILED
# Placeholder imports (assuming these will be imported from settings.py when running)
# from settings import MONGO_COLLECTION_DATA, MONGO_COLLECTION_URL, MONGO_COLLECTION_URL_FAILED

class ProductItem(DynamicDocument):
    """
    Template for storing extracted Product Data (Lidl API Fields).
    Maps to the MONGO_COLLECTION_DATA collection.
    """
    # meta = {"collection": MONGO_COLLECTION_DATA} 

    unique_id = StringField(required=True)
    product_name = StringField()
    brand = StringField()
    category = StringField()
    instock = BooleanField()
    regular_price = StringField()
    selling_price = StringField()
    promotion_type = StringField()
    pdp_url = StringField()
    currency = StringField()


class ProductUrlItem(DynamicDocument):
    """
    Template for storing URLs to be crawled (e.g., PDP URLs).
    Maps to the MONGO_COLLECTION_URL collection.
    """
    # meta = {"collection": MONGO_COLLECTION_URL}
    url = StringField(required=True)


class ProductFailedItem(DynamicDocument):
    """
    Template for storing URLs that failed to crawl.
    Maps to the MONGO_COLLECTION_URL_FAILED collection.
    """
    # meta = {"collection": MONGO_COLLECTION_URL_FAILED}
    url = StringField(required=True)
    error_type = StringField()

class LidlProductItem(DynamicDocument):
    """
    MongoDB schema for 126 fields (dynamic structure allowed).
    """
    meta = {'collection': 'lidl_products', 'db_alias': 'default'}

    unique_id = StringField()
    competitor_name = StringField()
    extraction_date = StringField()
    product_name = StringField()
    brand = StringField()
    grammage_quantity = StringField()
    grammage_unit = StringField()
    producthierarchy_level1 = StringField()
    producthierarchy_level2 = StringField()
    producthierarchy_level3 = StringField()
    producthierarchy_level4 = StringField()
    producthierarchy_level5 = StringField()
    producthierarchy_level6 = StringField()
    producthierarchy_level7 = StringField()
    regular_price = FloatField()
    price_was = FloatField()
    promotion_price = FloatField()
    promotion_type = StringField()
    currency = StringField()
    breadcrumb = StringField()  # full breadcrumb path as string
    pdp_url = StringField(uniqe=True)     # product detail page  
    product_description = StringField()
    file_name_1 = StringField()
    image_url_1 = StringField()
    file_name_2 = StringField()
    image_url_2 = StringField()
    file_name_3 = StringField()
    image_url_3 = StringField()
    site_shown_uom = StringField()
    instock = BooleanField()
    product_unique_key = StringField()
    