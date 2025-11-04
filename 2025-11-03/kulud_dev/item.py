from mongoengine import DynamicDocument, StringField, BooleanField, FloatField, DateTimeField
import datetime


class KuludProductItem(DynamicDocument):
    """Schema for validating parsed Kulud product details"""

    # meta = {"db_alias": "default", "collection": "kulud_product_details"}

    url = StringField(required=True)
    product_name = StringField()
    mrp = StringField()
    sale_price = StringField()
    discount = StringField()
    instock = BooleanField(default=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
