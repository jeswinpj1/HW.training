from mongoengine import DynamicDocument, StringField, FloatField

class ProductItem(DynamicDocument):
    """Schema for final product data"""

    meta = {"collection": "final_data"}  # optional; you can override in parser

    sku = StringField()
    company_name = StringField()
    manufacturer_name = StringField()
    brand_name = StringField()
    vendor_seller_part_number = StringField()
    item_name = StringField()
    full_product_description = StringField()
    price = StringField()  # keep as string if not guaranteed numeric
    unit_of_issue = StringField()
    qty_per_uoi = StringField()
    product_category = StringField()
    url = StringField()
    availability = StringField()
    manufacturer_part_number = StringField()
    country_of_origin = StringField()
    upc = StringField()
    model_number = StringField()
