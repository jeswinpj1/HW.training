from curl_cffi import requests
from pymongo import MongoClient
from parsel import Selector
from settings import logging,MONGO_DB,MONGO_COLLECTION_DATA,MONGO_COLLECTION_URL_FAILED,MONGO_COLLECTION_DETAILS

class Parser:
    def __init__(self):
        self.mongo = MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo[MONGO_DB]
   
    def start(self):
        """start code"""
        
        for doc in list(self.db[MONGO_COLLECTION_DATA].find()):
            url = doc.get("product_url")
            
            logging.info(f"Fetching: {url}")
            
            try:
                response = requests.get(url, impersonate="chrome")
                if response.status_code == 200:
                    self.parse_item(url, response, doc)
                else:
                    logging.warning(f"Failed: {response.status_code}")
                    self.db[MONGO_COLLECTION_URL_FAILED].insert_one({"url":url, 'status_code': response.status_code})
            except Exception as e:
                logging.error(f"Request error for {url}: {e}")
                self.db[MONGO_COLLECTION_URL_FAILED].insert_one({"url":url, 'error': e})
                
    def close(self):
        """connection close"""
        self.mongo.close()
    
    def parse_item(self, url, response, doc):
        """item part"""
        sel = Selector(text=response.text)
        
        # XPATH
        BREADCRUMBS_XPATH ='//ul[@class="cs-breadcrumbs__list"]//li//span//text()'
        TITLE_XPATH = '//h1[contains(@class,"page-title")]//span/text()'
        PRICE_RAW_XPATH = '//span[contains(@id,"product-price")]/@data-price-amount'
        PRICE_DISPLAY_XPATH = '//span[contains(@id,"product-price")]/span[@class="price"]/text()'
        OLD_PRICE_XPATH = '//span[contains(@class,"old-price")]//span[@class="price"]/text()'
        STOCK_XPATH ='//div[@class="pharmamarket-deliveryinformation"]//text()'
        IMAGE_URL_XPATH = '//div[@class="cs-page-product__gallery"]//picture//source/@srcset'
        DISCOUNT_XPATH = '//span[@class="cs-page-product__badge-text"]//text()'
        ATTRUBUTE_XPATH = '//table[@id="product-attribute-specs-table"]//tr'
        BRAND_XPATH = '//ul[@class="product-brand"]//img/@alt'
        DESCRIPTION_XPATH = '//div[@class="product attribute description"]//text()'
        
        # EXTRACT
        breadcrumbs_list = sel.xpath(BREADCRUMBS_XPATH).getall()
        title = sel.xpath(TITLE_XPATH).get()
        des=" ".join(sel.xpath(DESCRIPTION_XPATH).getall()).strip()
        
        # PRICE
        price_display = sel.xpath(PRICE_DISPLAY_XPATH).get()
        price_display = price_display.strip() if price_display and price_display.strip() else None

        old_price = sel.xpath(OLD_PRICE_XPATH).get()
        old_price = old_price.strip() if old_price and old_price.strip() else None

        if price_display and old_price:
            selling_price = f"{price_display} (Old Price: {old_price})"
        else:
            selling_price = price_display


        discount ="".join(sel.xpath(DISCOUNT_XPATH).getall()).strip()

        # STOCK (primary: <b>, fallback: text)
        stock = "".join(sel.xpath(STOCK_XPATH).getall())


        images = sel.xpath(IMAGE_URL_XPATH).getall()
        if not images:
            images = sel.xpath('//div[@class="cs-page-product__gallery"]//picture//img/@src').getall()
        images = list(set(images))

        attributes = {}
        rows = sel.xpath(ATTRUBUTE_XPATH)
        for r in rows:
            key = r.xpath('./th/text()').get()
            value = r.xpath('./td/text()').get()
            if key and value:
                attributes[key.strip()] = value.strip()

        brand = sel.xpath(BRAND_XPATH).get()

        breadcrumbs = " > ".join(breadcrumbs_list) if breadcrumbs_list else ""
        
      

        
        # ITEM YIELD
        item = {}
        item["product_url"] = url
        item["breadcrumbs"] = breadcrumbs
        item["product_name"] = title
        item["stock"] = stock
        item["brand"] = brand
        item["attributes"] = attributes
        item["discount"] = discount
        item["selling_price"] = selling_price
        item["regular_price"] = old_price
        item["images"] = images
        item["description"] = des
        
        logging.info(item)
        
        try:
            self.db[MONGO_COLLECTION_DETAILS].insert_one(item)
            logging.info(" Saved product details")
        except Exception as e:
            pass


if __name__ == "__main__":
    parser_obj = Parser()
    parser_obj.start()
    parser_obj.close()