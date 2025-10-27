from mongoengine import DynamicDocument, StringField, FloatField, IntField, BooleanField
from settings import  MONGO_COLLECTION_DATA
class LidlProductItem(DynamicDocument):
    """
    MongoDB schema for 126 fields (dynamic structure allowed).
    """
    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_DATA}

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
    
