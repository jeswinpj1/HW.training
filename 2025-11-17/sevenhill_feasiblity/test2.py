import json
import requests
from parsel import Selector
import time

# --- CONFIGURATION ---
INPUT_FILE = "sevenhills_products.json"
OUTPUT_FILE = "sevenhills_vehicle_data.json"
URL_LIMIT = 500

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def run_scraper():
    try:
        with open(INPUT_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return

    all_urls = []
    for category, urls in data.items():
        all_urls.extend(urls)
    
    all_urls = list(set(all_urls))
    
    # Apply Limit
    if len(all_urls) > URL_LIMIT:
        all_urls = all_urls[:URL_LIMIT]
        print(f"Limit applied: Processing only first {URL_LIMIT} URLs.")
    
    extracted_data = []
    success_count = 0
    failure_count = 0

    print(f"Starting scrape for {len(all_urls)} vehicles...\n")

    for i, url in enumerate(all_urls):
        print(f"[{i+1}/{len(all_urls)}] Processing: {url}")
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                print(f"  -> Failed (Status {resp.status_code})")
                failure_count += 1
                continue

            sel = Selector(resp.text)
            
            # 1. Title Parsing
            page_title = sel.xpath("normalize-space(//h1/text() | //title/text())").get().split("|")[0].strip()
            
            year, make, model = "N/A", "N/A", "N/A"
            title_parts = page_title.split(" ", 2)
            if len(title_parts) >= 1 and title_parts[0].isdigit():
                year = title_parts[0]
                if len(title_parts) >= 2: make = title_parts[1]
                if len(title_parts) >= 3: model = title_parts[2]
            
            # 2. Fields Extraction (Updated for <dt>/<dd> structure)
            item = {
                "source_link": url,
                "full_title": page_title,
                "year": year,
                "make": make,
                "model": model,
                # Strategy: Find <dt> with label, grab the following <dd> text
                "vin": sel.xpath('normalize-space(//dt[contains(., "Vin")]/following-sibling::dd/text())').get(default=""),
                "stock_no": sel.xpath('normalize-space(//dt[contains(., "Stock")]/following-sibling::dd/text())').get(default=""),
                "price": sel.xpath('normalize-space(//dt[contains(., "Price")]/following-sibling::dd/text())').get(default="Call for Price"),
                "mileage": sel.xpath('normalize-space(//dt[contains(., "Miles")]/following-sibling::dd/text())').get(default=""),
                "transmission": sel.xpath('normalize-space(//dt[contains(., "Transmission")]/following-sibling::dd/text())').get(default=""),
                "engine": sel.xpath('normalize-space(//dt[contains(., "Engine")]/following-sibling::dd/text())').get(default=""),
                "exterior_color": sel.xpath('normalize-space(//dt[contains(., "Exterior")]/following-sibling::dd/text())').get(default=""),
                "interior_color": sel.xpath('normalize-space(//dt[contains(., "Interior")]/following-sibling::dd/text())').get(default=""),
                "body_style": sel.xpath('normalize-space(//dt[contains(., "Body Style")]/following-sibling::dd/text())').get(default=""),
                
                # Description and Images usually remain outside the DL list
                "description": sel.xpath('normalize-space(//div[contains(@id, "description") or contains(@class, "vehicle-description")])').get(default=""),
                "image_urls": sel.xpath('//div[contains(@class, "vehicle-photos")]//img/@src | //a[contains(@class, "gallery")]/@href').getall()
            }
            
            extracted_data.append(item)
            success_count += 1
            
        except Exception as e:
            print(f"  -> Error: {e}")
            failure_count += 1

    with open(OUTPUT_FILE, "w") as f:
        json.dump(extracted_data, f, indent=4)

    # --- SUMMARY REPORT ---
    total = success_count + failure_count
    success_rate = (success_count / total * 100) if total > 0 else 0
    failure_rate = (failure_count / total * 100) if total > 0 else 0

    print("\n" + "="*30)
    print("SCRAPING SUMMARY")
    print("="*30)
    print(f"Total Requests: {total}")
    print(f"Success:        {success_count}")
    print(f"Failure:        {failure_count}")
    print(f"Success Rate:   {success_rate:.2f}%")
    print(f"Failure Rate:   {failure_rate:.2f}%")
    print("="*30)
    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_scraper()