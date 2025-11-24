from mongoengine import Document, StringField, DictField,ListField
from settings import MONGO_DB, MONGO_COLLECTION_SUBCATEGORIES, MONGO_COLLECTION_PRODUCT_URLS,MONGO_COLLECTION_PRODUCT_DATA
# Connect to the database specified in settings

class SubcategoryItem(Document):
    """MongoDB model to load subcategory details."""
    subcat_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    text = StringField()
    category_url = StringField()
    meta = {'collection': MONGO_COLLECTION_SUBCATEGORIES}


class ProductURLItem(Document):
    """MongoDB model for storing scraped product URLs."""
    url = StringField(required=True, unique=True)
    subcat_id = StringField()
    subcat_name = StringField()
    meta = {'collection': MONGO_COLLECTION_PRODUCT_URLS}

class ProductItem(Document):
    """
    MongoDB model for storing scraped product details.
    This structure is based on the fields extracted in the parse_item logic.
    """
    url = StringField(required=True, unique=True)
    product_id = StringField()
    product_name = StringField()
    product_type = StringField()

    # Pricing fields
    price = StringField()
    wasPrice = StringField()        # FIXED: Correct field name (capital P)
    discount = StringField()
    
    # Stock/Quantity
    stock = StringField()
    quantity = StringField()
    
    # Text/Description fields
    details_string = StringField()

    # Additional fields found from HTML parsing
    product_color = StringField()
    material = StringField()
    breadcrumb = ListField(StringField())

    # Complex fields
    specification = DictField()
    image = ListField(StringField())

    meta = {'collection': MONGO_COLLECTION_PRODUCT_DATA}