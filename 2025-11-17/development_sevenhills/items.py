from mongoengine import DynamicDocument, StringField, BooleanField, DictField, ListField, IntField, FloatField, DateTimeField
import datetime
from settings import MONGO_COLLECTION_DATA
class ProductItem(DynamicDocument):
    """
    Main Vehicle Data Schema for Seven Hills Motorcars.
    Stores all technical specifications and listing details.
    """
    meta = {"db_alias": "default", "collection": MONGO_COLLECTION_DATA}

    # -- Standard Metadata --
    url = StringField(required=True)  # This is the Source Link
    project_name = StringField(default="sevenhills_scraper")
    crawled_date = DateTimeField(default=datetime.datetime.utcnow)
    
    # -- Vehicle Identification --
    make = StringField()
    model = StringField()
    year = StringField()      # Keeping as String to handle cases like "1969 1/2"
    vin = StringField()       # Vehicle Identification Number
    stock_no = StringField()  # Internal Stock Number

    # -- Pricing & Specs --
    price = StringField()     # stored as string to keep currency symbols (e.g. "$19,500")
    mileage = StringField()   # stored as string (e.g. "45,867")
    transmission = StringField()
    engine = StringField()
    fuel_type = StringField()
    body_style = StringField()

    # -- Aesthetics --
    exterior_color = StringField()
    interior_color = StringField()
    
    # -- Content --
    description = StringField()
    image_urls = ListField(StringField())  # List of image source links

    # -- Dynamic Fields --
    # The 'DynamicDocument' inheritance allows you to add extra fields 
    # on the fly without defining them here if the website changes.


class ProductUrlItem(DynamicDocument):
    """Stores discovered product URLs to be scraped"""
    # meta = {"db_alias": "default", "collection": MONGO_COL_URL}
    url = StringField(required=True)
    status = StringField(default="pending")


class ProductMismatchItem(DynamicDocument):
    """Logs items where data extraction might be incorrect"""
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_MISMATCH}
    url = StringField()
    input_style = StringField(required=True)


class ProductEmptyItem(DynamicDocument):
    """Logs items that returned no data"""
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_EMPTY}
    url = StringField()
    input_style = StringField(required=True)


class ProductCountItem(DynamicDocument):
    """Logs zip codes or inventory counts if applicable"""
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_COUNT}
    zipcode = StringField(required=True)


class ProductResponseItem(DynamicDocument):
    """Logs raw responses or debug info"""
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_RESPONSE}
    url = StringField(required=True)
    status_code = IntField()


class ProductFailedItem(DynamicDocument):
    """Logs URLs that failed completely (404, 500, Timeout)"""
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_URL_FAILED}
    url = StringField(required=True)
    error_msg = StringField()


class ProductCategoryUrlItem(DynamicDocument):
    """Stores Category URLs (e.g., /vehicles/sold)"""
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_CATEGORY}
    url = StringField(required=True)


class ProductPageItem(DynamicDocument):
    """Stores Pagination URLs"""
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_PAGINATION}
    url = StringField(required=True)