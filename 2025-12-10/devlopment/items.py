from mongoengine import DynamicDocument, StringField, ListField, IntField, FloatField, DictField

class ProductItem(DynamicDocument):
    """initializing URL fields and its Data-Types for matched products"""

    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_DATA}
    
    # Fields based on the output you are inserting
    match_type = StringField()     # e.g., "NAME EXACT", "NAME PARTIAL"
    score = IntField()             # Fuzzy score
    product_name = StringField()   # Matched product name
    product_url = StringField()    # Matched product URL
    input_id = StringField()       # The original input document ID for traceability


class ProductUrlItem(DynamicDocument):
    """Placeholder for URL items (not used in your logic)"""

    # meta = {"db_alias": "default", "collection": MONGO_COL_URL}
    url = StringField(required=True)


class ProductFailedItem(DynamicDocument):
    """Placeholder for failed search inputs"""

    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_URL_FAILED}
    url = StringField(required=True)


# Keep other template classes for completeness, though they are not used in your logic
class ProductMismatchItem(DynamicDocument):
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_MISMATCH}
    input_style = StringField(required=True)

class ProductEmptyItem(DynamicDocument):
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_EMPTY}
    input_style = StringField(required=True)

class ProductCountItem(DynamicDocument):
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_COUNT}
    zipcode = StringField(required=True)

class ProductResponseItem(DynamicDocument):
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_RESPONSE}
    url = StringField(required=True)

class ProductCategoryUrlItem(DynamicDocument):
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_CATEGORY}
    url = StringField(required=True)

class ProductPageItem(DynamicDocument):
    # meta = {"db_alias": "default", "collection": MONGO_COLLECTION_PAGINATION}
    url = StringField(required=True)