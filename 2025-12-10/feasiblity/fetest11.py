from curl_cffi import requests
from parsel import Selector
from pymongo import MongoClient, errors
import time

# -------------------------------
# MongoDB Setup
# -------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["pharmamarket_db"]
output_col = db["output"]   # URLs to scrape
data_col = db["data"]       # save extracted product details

# Create unique index to avoid duplicates
data_col.create_index("product_url", unique=True)

# -------------------------------
# Extraction function
# -------------------------------
def extract_details(html):
    sel = Selector(text=html)

    title = sel.xpath('//h1[contains(@class,"page-title")]//span/text()').get()
    title = title.strip() if title else None

    price_raw = sel.xpath('//span[contains(@id,"product-price")]/@data-price-amount').get()
    price_display = sel.xpath('//span[contains(@id,"product-price")]/span[@class="price"]/text()').get()
    old_price = sel.xpath('//p[@class="old-price"]//span[@class="price"]/text()').get()
    if old_price and price_display:
        price_display = f"{price_display} (Old Price: {old_price})"

    stock = sel.xpath('//div[@class="pharmamarket-deliveryinformation"]/b/text()').get()
    image_url = sel.xpath('//div[contains(@class,"fotorama__stage__frame")]//img/@src').get()
    discount = "".join(sel.xpath('//span[@class="cs-page-product__badge-text"]//text()').getall()).strip()
    breadcrumbs = sel.xpath('//ul[@class="cs-breadcrumbs__list"]//li//span//text()').getall()
    desc = " ".join(sel.xpath('//div[@class="product attribute description"]//text()').getall()).strip()

    images = sel.xpath('//div[@class="cs-page-product__gallery"]//picture//source/@srcset').getall()
    if not images:
        images = sel.xpath('//div[@class="cs-page-product__gallery"]//picture//img/@src').getall()
    images = list(set(images))

    attributes = {}
    rows = sel.xpath('//table[@id="product-attribute-specs-table"]//tr')
    for r in rows:
        key = r.xpath('./th/text()').get()
        value = r.xpath('./td/text()').get()
        if key and value:
            attributes[key.strip()] = value.strip()

    brand = sel.xpath('//ul[@class="product-brand"]//img/@alt').get()

    return {
        "title": title,
        "price_raw": price_raw,
        "old_price": old_price,
        "price_display": price_display,
        "stock": stock,
        "description": desc,
        "attributes": attributes,
        "brand": brand,
        "breadcrumbs": breadcrumbs,
        "discount": discount,
        "images": images,
        "image_main": image_url
    }

# -------------------------------
# Main scraping loop with deduplication
# -------------------------------
def scrape_products():
    urls_cursor = output_col.find({}, {"product_url": 1})

    for item in urls_cursor:
        url = item.get("product_url")
        if not url:
            continue

        # Check if URL already exists in data collection
        if data_col.find_one({"product_url": url}):
            print(f"Skipped (already scraped): {url}")
            continue

        try:
            response = requests.get(url, impersonate="chrome")
            if response.status_code == 200:
                data = extract_details(response.text)
                data["product_url"] = url
                try:
                    data_col.insert_one(data)
                    print(f"Saved: {url}")
                except errors.DuplicateKeyError:
                    print(f"Duplicate detected (skipped): {url}")
            else:
                print(f"Failed to fetch: {url} | Status: {response.status_code}")

            time.sleep(1)  # polite delay between requests
        except Exception as e:
            print(f"Error fetching {url}: {e}")

if __name__ == "__main__":
    scrape_products()
