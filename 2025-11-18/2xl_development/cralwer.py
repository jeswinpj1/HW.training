import logging
import json
import requests
from time import sleep
from lxml import html
from parsel import Selector  
from pymongo import MongoClient
from settings import HEADERS, COOKIES, API_TEMPLATE, MONGO_URI, MONGO_DB, MONGO_COLLECTION_SUBCATEGORIES
from item import SubcategoryItem, ProductURLItem
from mongoengine import connect, disconnect


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ProductURLCrawler:
    """Crawling Product URLs based on Subcategory API endpoints"""

    def __init__(self):
 
        self.mongo =connect(db=MONGO_DB, host="localhost", alias= "default")
        self.queue = None  

    def start(self):
        """Fetches subcategories and initiates URL requests"""
 
        try:
            subcategories = SubcategoryItem.objects.all()
            logging.info(f"Found {len(subcategories)} subcategories to process from '{MONGO_COLLECTION_SUBCATEGORIES}' collection.")
        except Exception as e:
            logging.error(f"Error fetching subcategories from DB: {e}")
            return
            
        for subcat in subcategories:
            subcat_id = subcat.subcat_id
            subcat_name = subcat.name
            slug = subcat_name.lower().replace(" ", "-") 
            
            meta = {
                'subcat_id': subcat_id,
                'subcat_name': subcat_name,
                'slug': slug,
            }
            
            logging.info(f"\n=== SUBCATEGORY: {subcat_name} ({subcat_id}) ===")
            
            page = 1 
            api_url = API_TEMPLATE.format(slug=slug, page=page, subcat_id=subcat_id)
            meta["page"] = page # initialising page for pagination in meta, matching template structure
            
            while True:
                api_url = API_TEMPLATE.format(slug=slug, page=page, subcat_id=subcat_id)
                logging.info(f"[PAGE {page}] {api_url}")
                
                try:
                    response = requests.get(api_url, headers=HEADERS, cookies=COOKIES, timeout=30)
                    response.raise_for_status() # Raises an exception for bad status codes

                    is_next = self.parse_item(response, meta)
                    
                    if not is_next:
                        logging.info(f"Pagination completed for {subcat_name}")
                        break
                    page += 1
                    meta["page"] = page
                    sleep(1) 
                except requests.exceptions.RequestException as e:
                    logging.error(f" Error fetching page {page} for {subcat_name}: {e}")
                    break
                except Exception as e:
                     logging.error(f"An unexpected error occurred: {e}")
                     break

    def parse_item(self, response, meta):
        """Parses the API response to extract product URLs and handles pagination check."""

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON response for {meta.get('subcat_name')} (Page {meta.get('page')}): {e}")
            return False

        # Extract HTML section as per your logic
        product_html = data.get("sections", {}).get("product_list", "")
        
        if not product_html:
            logging.warning(" No 'product_list' section found or page finished.")
            return False # No more products/next page
        
        tree = html.fromstring(product_html)
        PRODUCT_XPATH = '//a[@href]' # XPath to find all links in the product list
        URL_XPATH = '/@href'         # Attribute to extract
        
        # EXTRACT (Adapting the template's extraction to your logic)
        product_links = tree.xpath(f"{PRODUCT_XPATH}{URL_XPATH}")
        
        # Check for presence of next page (total_pages check from your logic)
        total_pages = data.get("total_pages", 1)
        current_page = meta.get("page", 1)
        
        if not product_links:
             logging.warning("No product links extracted on this page.")
             return False
             
        for link in product_links:
            # ITEM YEILD (Inserting the extracted URL into the database using mongoengine model)
            item = {}
            item['url'] = link
            item['subcat_id'] = meta.get('subcat_id')
            item['subcat_name'] = meta.get('subcat_name')
            
            logging.debug(item) # Use debug for high volume items
            try:
                # Using the mongoengine model from item.py
                product_item = ProductURLItem(**item)
                product_item.save()
                    
            except Exception as e:
                # Template uses a bare 'except:' which is generally discouraged, but kept for structure
                logging.error(f"Error inserting/updating item: {link}. Error: {e}")
                pass # Continue to next item

        logging.info(f" → Extracted {len(product_links)} links. Total Pages: {total_pages}")
        
        # Pagination check
        if current_page >= total_pages:
            logging.info(f" Finished: reached last page ({total_pages})")
            return False # Signal to stop pagination
        
        return True # Signal to continue to the next page

    def close(self):
        """Close function for all module object closing"""
        self.mongo.close()

if __name__ == "__main__":
   
    crawler = ProductURLCrawler()
    crawler.start()
    crawler.close()