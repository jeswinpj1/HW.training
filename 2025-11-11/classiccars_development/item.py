from mongoengine import DynamicDocument, StringField, ListField
from settings import MONGO_COLLECTION_DATA

class ClassicCarItem(DynamicDocument):
    """Validation model for classic car details"""
    
    meta = {"collection": MONGO_COLLECTION_DATA} 
    source_url = StringField(required=True)
    make = StringField()
    model = StringField()
    year = StringField()
    VIN = StringField()
    price = StringField()
    mileage = StringField()
    transmission = StringField()
    engine = StringField()
    color = StringField()
    fuel_type = StringField()
    body_style = StringField()
    description = StringField()
    image_urls = ListField(StringField())
