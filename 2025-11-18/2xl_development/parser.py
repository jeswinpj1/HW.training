import logging
import json
import requests
from time import sleep
from parsel import Selector
from pymongo import MongoClient
from mongoengine import connect
from settings import HEADERS, MONGO_DB, MONGO_COLLECTION_PRODUCT_URLS
from item import ProductURLItem, ProductItem 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Parser:
    """Product Detail Parser based on URLs from DB"""

    def __init__(self):
        self.mongo =connect(db=MONGO_DB, host="localhost", alias= "default")
        self.queue = None  

    def start(self):
        """Fetches product URLs from DB, requests pages, and initiates parsing"""

        logging.info(f"Fetching URLs from '{MONGO_COLLECTION_PRODUCT_URLS}'...")

        for item in ProductURLItem.objects():
            url = item.url
            try:
                resp = requests.get(url, headers=HEADERS, timeout=30)
                if resp.status_code != 200:
                    logging.error(f"Failed to fetch: {url}. Status: {resp.status_code}")
                    continue # Skip to the next URL on failure
                
                # Pass the URL and the successful response object to the parser
                self.parse_item(url, resp) 
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching URL {url}: {e}")
            
            sleep(0.1) # Small polite delay

        logging.info("Product detail parsing completed.")
    
    def close(self):
       self.mongo.close()

    def parse_item(self, url, resp): 
        """item part: Fetches product page and extracts details (Your main parsing logic)"""

        sel = Selector(resp.text)
    
        # XPATHS
        PRODUCT_NAME_XPATH = "//h1[@class='page-title']//span[@itemprop='name']/text()"
        PRODUCT_ID_XPATH = "//div[contains(@class,'price-box')]/@data-product-id" # only inside the script 
        PRODUCT_TYPE_XPATH = "//div[@itemprop='sku']/text()"
        PRICE_XPATH = "//span[contains(@id,'product-price')]/span/text()"
        WAS_PRICE_XPATH = "//span[contains(@id,'old-price')]/span/text()"
        DISCOUNT_XPATH = "//span[contains(@class,'discountper')]/text()"
        STOCK_XPATH = "//div[contains(@class,'stock')]/span/text()"
        QUANTITY_XPATH = "//input[@name='qty']/@value"
        IMAGES_XPATH = "//div[@class='MagicToolboxSelectorsContainer']//img/@src"
        BREADCRUMB = ("//ul[@class='items']/li//text()") 
        SPEC_ROW = "//div[contains(@class,'detail-acc')]//div[@class='value']"

        # BASIC EXTRACT
        product_id = sel.xpath(PRODUCT_ID_XPATH).get()
        product_name = sel.xpath(PRODUCT_NAME_XPATH).get()
        product_type = sel.xpath(PRODUCT_TYPE_XPATH).get()
        price = sel.xpath(PRICE_XPATH).get()
        wasprice = sel.xpath(WAS_PRICE_XPATH).get()
        discount = sel.xpath(DISCOUNT_XPATH).get()
        stock = sel.xpath(STOCK_XPATH).get()
        quantity = sel.xpath(QUANTITY_XPATH).get()
        breadcrumbs = [b.strip() for b in sel.xpath(BREADCRUMB).getall() if b.strip()]
        if not breadcrumbs:
            breadcrumbs = ["Home"]
            script_text = sel.xpath("//script[@type='text/x-magento-init']/text()").getall()
            for script_text in script_text:
                if ".breadcrumbs" in script_text: 
                    product_from_script = json.loads(script_text).get(".breadcrumbs", {}).get("breadcrumbs", {}).get("product")
                    print(script_text)
                    if product_from_script:
                        breadcrumbs.append(product_from_script.strip())
                
        images = sel.xpath(IMAGES_XPATH).getall()
        # SPECIFICATION PARSE
        specification = {}
        spec_rows = sel.xpath(SPEC_ROW)

        for row in spec_rows:
            key = row.xpath("./strong/text()").get()
            val_list = row.xpath("./text()").getall()

            if key:
                key = key.replace(":", "").strip()
                val = " ".join([v.strip() for v in val_list if v.strip()])
                specification[key] = val

        # DETAILS DESCRIPTION
        details_text_list = sel.xpath("//div[@id='description']//text()").getall()
        details_string = " ".join([t.strip() for t in details_text_list if t.strip()])

        # COLOR & MATERIAL
        product_color = specification.get("Color", "")
        material = specification.get("Material", "")

        # FINAL ITEM
        item = {
            "url": url,
            "product_id": product_id,
            "product_name": product_name,
            "product_type": product_type,
            "price": price,
            "wasPrice": wasprice,
            "discount": discount,
            "stock": stock,
            "quantity": quantity,
            "specification": specification,
            "details_string": details_string,
            "product_color": product_color,
            "material": material,
            "breadcrumb": breadcrumbs,
            "image": images,
        }
        
        
        logging.info(item)
        
        try:
            # Using the mongoengine model from item.py.save()
            ProductItem(
                **item # Passing the dictionary directly
            ).save()
        except Exception as e:
            logging.error(f"Error saving item {product_name}: {e}")
            pass 

        except Exception as e:
            logging.error(f"Error parsing {url}: {e}")
            

if __name__ == "__main__":
    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()