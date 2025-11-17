from mongoengine import DynamicDocument, StringField, FloatField, ListField

class ProductItem(DynamicDocument):
    """Main product item - Contains both Generic and Sephora specific fields"""
    
    # Generic Fields
    url = StringField()
    product_name = StringField()
    brand = StringField()
    currency = StringField()
    review_dict_list = ListField()

    # Sephora Specific Fields (Required for Parser)
    retailer_id = StringField()
    retailer = StringField()
    grammage_quantity = StringField()
    grammage_unit = StringField()
    original_price = FloatField()
    selling_price = FloatField()
    promotion_description = StringField()
    pdp_url = StringField()
    image_url = StringField()
    ingredients = StringField()
    directions = StringField()
    disclaimer = StringField()
    description = StringField()
    diet_suitability = StringField()
    colour = StringField()
    hair_type = StringField()
    skin_type = ListField()
    skin_tone = StringField()

class ProductUrlItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""
    url = StringField(required=True)

class ProductMismatchItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""
    input_style = StringField(required=True)

class ProductEmptyItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""
    input_style = StringField(required=True)

class ProductCountItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""
    zipcode = StringField(required=True)

class ProductResponseItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""
    url = StringField(required=True)

class ProductFailedItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""
    url = StringField(required=True)

class ProductCategoryUrlItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""
    url = StringField(required=True)

class ProductPageItem(DynamicDocument):
    """initializing URL fields and its Data-Types"""
    url = StringField(required=True)