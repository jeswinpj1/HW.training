from pymongo import MongoClient
from mongoengine import DynamicDocument, StringField, connect
from settings import MONGO_DB_NAME, MONGO_URI

# optional: mongoengine connection if you use mongoengine models
try:
    connect(MONGO_DB_NAME, host=MONGO_URI)
except Exception:
    # If mongoengine not available or connection not desired, scripts still use pymongo
    pass

MONGO_COLLECTION_DATA = "product_data"
MONGO_COLLECTION_ENRICHED_DATA = "full126field_product_data"


class ProductItem(DynamicDocument):
    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_DATA}
    unique_id = StringField(required=True)
    product_name = StringField()
    brand = StringField()
    regular_price = StringField()
    currency = StringField()
    pdp_url = StringField()


class ProductEnrichedItem(DynamicDocument):
    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_ENRICHED_DATA}
    unique_id = StringField(required=True)
    product_name = StringField()
    # Define additional fields as needed; dynamic document allows extra fields
