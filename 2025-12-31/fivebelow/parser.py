import requests
import json
from parsel import Selector
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0"}
INPUT_FILE = "/home/user/HW.training/fivebelow_product_urls.txt"
OUTPUT_FILE = "/home/user/HW.training/fivebelow_products_cheking.json"

# Read URLs
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    product_urls = [line.strip() for line in f if line.strip()]

def parse_product(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    sel = Selector(text=r.text)

    data = {
        "id": sel.xpath('//input[@name="productId"]/@value').get(default="") or url.split("-")[-1],
        "url": url,
        "title": sel.xpath('//div[@class="relative flex pr-40"]/h1/text()').get(default="").strip(),
        "price": sel.xpath('(//p[contains(@class,"text-fivebelow-blue")])[1]/text()').get(default="").strip().replace("$",""),
        "images": list(dict.fromkeys(sel.xpath('//div[contains(@class,"relative")]/div/img/@src').getall())),
        "sku": sel.xpath('string(//span[contains(@class,"my-10")])').get(default="").replace("item #","").strip(),
        "description_items": [item.strip() for item in sel.xpath('//div[contains(@id,"headlessui-disclosure-panel")]//ul/li/text()').getall() if item.strip()]
    }
    return data

# Parse and save 1 by 1
for idx, url in enumerate(product_urls, 1):
    try:
        print(f"[{idx}/{len(product_urls)}] Scraping {url}")
        product_data = parse_product(url)
        
        # Append each product JSON immediately
        with open(OUTPUT_FILE, "a", encoding="utf-8") as jf:
            json.dump(product_data, jf, ensure_ascii=False)
            jf.write("\n")
            
    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")

print(f"\n✅ Done! Scraped {len(product_urls)} products and saved to {OUTPUT_FILE}")
