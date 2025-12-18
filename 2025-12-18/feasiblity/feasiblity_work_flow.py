import requests
import json
import time
from scrapy import Selector
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["biggestbook"]
collection = db["products"]

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'X-API-KEY': '31BC6E02FD51DF7F7CE37186A31EE9B9DEF9C642526BC29F8201D81B669B9',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://www.biggestbook.com',
    'Referer': 'https://www.biggestbook.com/',
}

BASE_URL = "https://api.essendant.com/digital/digitalservices/search/v2/search"

############################## CRAWLER (Categories) ##############################
def get_categories():
    params = {'fc': '0', 'cr': 1, 'rs': 1, 'st': 'BM', 'cmt': 'ALT', 'vc': 'n'}
    try:
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
        data = response.json()
        category_list = []
        facets = data.get('searchResult', {}).get('appliedFacets', [])
        for facet in facets:
            if facet.get('name') == "Category":
                for val in facet.get('values', []):
                    category_list.append({
                        'id': val.get('id'),
                        'name': val.get('description') or "Unknown"
                    })
        return category_list
    except Exception as e:
        return []

############################## PARSER (Products) ##############################
def parse_and_save_products(category):
    fc = category['id']
    cat_name = category['name']
    cr = 1
    rs = 24
    
    while True:
        params = {'fc': fc, 'cr': cr, 'rs': rs, 'st': 'BM', 'cmt': 'ALT', 'vc': 'n'}
        response = requests.get(BASE_URL, headers=headers, params=params)
        
        if response.status_code != 200:
            break
            
        data = response.json()
        products = data.get('searchResult', {}).get('products', [])
        page_context = data.get('searchResult', {}).get('pageContext', {})
        available_results = page_context.get('availableResults', 0)

        if not products:
            break

        for p in products:
            # Data Normalization
            item = {
                "win": p.get("win"),
                "mpn": p.get("mpn"),
                "brand_name": p.get("brand", {}).get("description"),
                "description": p.get("description"),
                "price": p.get("actualPrice"),
                "image_url": p.get("image", {}).get("url"),
                "category_name": cat_name,
                "category_id": fc,
                "metadata": {
                    "weight": p.get("weight"),
                    "uom": p.get("uom"),
                    "unspsc": p.get("unspsc")
                }
            }
            if item["win"]:
                collection.update_one({"win": item["win"]}, {"$set": item}, upsert=True)
        
        cr += rs
        if cr > available_results:
            break
        time.sleep(1) # Polite delay

############################## EXECUTION ##############################
if __name__ == "__main__":
    all_categories = get_categories()
    for category in all_categories:
        parse_and_save_products(category)

    client.close()

"""
FINDINGS & FEASIBILITY:
- [PAGINATION]: Uses 'cr' (cursor) and 'rs' (result size). Deep paging limits may apply.
- [MISSING DATA]: URL does not change with color/variants; variants must be parsed from 'raw' JSON.
- [AUTH]: X-API-KEY is static but may rotate; requires monitoring.
"""