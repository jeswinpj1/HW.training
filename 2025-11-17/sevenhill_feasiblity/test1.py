import requests
from parsel import Selector
from urllib.parse import urljoin
import json

BASE_URL = "https://www.sevenhillsmotorcars.com"

# Main category URLs
category_map = {
    "/vehicles": "current_inventory",
    "/vehicles/sold": "sold_inventory"
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
}

def get_product_urls(category_url):
    """Collect all product URLs in a main category with pagination."""
    product_urls = []
    next_page = category_url

    while next_page:
        full_url = urljoin(BASE_URL, next_page)
        print(f"Fetching: {full_url}")
        
        try:
            resp = requests.get(full_url, headers=headers, timeout=10)
        except Exception as e:
            print(f"Error fetching {full_url}: {e}")
            break

        if resp.status_code != 200:
            print(f"Failed to fetch {next_page}: Status {resp.status_code}")
            break

        sel = Selector(resp.text)
        
        # Extract product URLs
        urls = sel.xpath('//div[contains(@class,"sh-vehicle-row")]//a[@class="sh-inventory-item"]/@href').getall()
        product_urls.extend([urljoin(BASE_URL, u) for u in urls])
        
        # --- PAGINATION FIX ---
        # 1. Find the <li> that contains 'next_page' in its class (handles trailing spaces)
        next_li = sel.xpath('//ul[contains(@class,"pagination")]/li[contains(@class, "next_page")]')
        
        # 2. Check if that <li> exists and does NOT have "disabled" in its class
        if next_li and "disabled" not in (next_li.attrib.get('class', '')):
            # 3. Extract the href
            next_page_href = next_li.xpath('./a/@href').get()
            if next_page_href and next_page_href != "#":
                next_page = next_page_href
            else:
                next_page = None
        else:
            next_page = None
        # ----------------------

    return product_urls

if __name__ == "__main__":
        
    all_products = {}
    for cat in category_map.keys(): 
        print(f"Processing category: {cat}")
        urls = get_product_urls(cat)
        print(f"Found {len(urls)} products in {cat}")
        all_products[category_map[cat]] = urls 

    # Save to JSON
    with open("sevenhills_products.json", "w") as f:
        json.dump(all_products, f, indent=4)
        
    print("Saved all product URLs to sevenhills_products.json")

    