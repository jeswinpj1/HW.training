import logging
import json
from parsel import Selector
from settings import HEADERS, MONGO_DB, MONGO_COLLECTION_DATA ,MONGO_COLLECTION_INPUT
from items import ProductItem
from curl_cffi import requests
from fuzzywuzzy import fuzz
import urllib.parse
from pymongo import MongoClient


class Crawler:
    """Crawling Urls and matching products"""
   
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.mongo = self.client[MONGO_DB]

    def start(self):
        """Requesting Start url and iterating over input data"""

        input_items = self.mongo[MONGO_COLLECTION_INPUT].find({})

        for item in input_items:
            meta = {
                'EAN MASTER': str(item.get("EAN MASTER", "")).strip(),
                'CNK BELUX': str(item.get("CNK BELUX", "")).strip(),
                'PRODUCT GENERAL NAME': str(item.get("PRODUCT GENERAL NAME", "")).strip(),
                '_id': item.get("_id")
            }

            input_name = meta.get('PRODUCT GENERAL NAME')

            if not input_name:
                logging.warning(f"Skipping item with no PRODUCT GENERAL NAME: {meta.get('_id')}")
                continue

            logging.info(f"\nProcessing: {input_name}")

            encoded_search = urllib.parse.quote_plus(input_name)
            api_url = f"https://www.pharmamarket.be/be_fr/insider/search/query/?q={encoded_search}"

            try:
                response = requests.get(
                    api_url,
                    headers=HEADERS,
                    impersonate="chrome"
                )

                if response.status_code != 200:
                    logging.error(
                        f"Failed to fetch search results for '{input_name}'. "
                        f"Status: {response.status_code}"
                    )
                    continue

                # pass response + meta to parser
                self.parse_item(meta, response)

            except Exception as e:
                logging.error(f"Request error for {input_name}: {e}")



    def parse_item(self, meta, response):
        """item part - Performing search and fuzzy matching"""

        input_name = meta.get('PRODUCT GENERAL NAME')
        sel = Selector(response.text)
        products = sel.xpath('//a[@class="cs-product-tile__name-link product-item-link"]')
        
        exact = None
        partial = []
        for p in products:
            name = p.xpath("text()").get()
            product_url = p.xpath("./@href").get()
            
            if not name or not product_url or "api" in product_url:
                continue
            
            
            score = fuzz.token_sort_ratio(input_name.upper(), name.upper())

            item={}
            item["product_url"]=product_url
            item["product_name"]=name
            
            
            if score == 100:
                item['match_type'] = "NAME EXACT"
                item['score'] = score
                exact = item
                break
            elif 70 <= score < 100:
                item['match_type'] = "NAME PARTIAL"
                item['score'] = score
                partial.append(item)

        

        if exact:
            logging.info(exact)
            try:
                self.mongo[MONGO_COLLECTION_DATA].insert_one(exact)
                logging.info(" Saved exact name match")
            except: 
                pass
                
        elif partial:
            logging.info(partial)
            try:
                self.mongo[MONGO_COLLECTION_DATA].insert_many(partial)
                logging.info(f" Saved {len(partial)} partial name matches")
            except:
                logging.error
                
        else:
            logging.warning(" No name match found")


    def close(self):
        """Close function for all module object closing"""
        self.client.close()

if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()
    crawler.close()

