import json
import requests
from lxml import html
import time
import os

INPUT_FILE = "emlakjet_product_urls.json"
OUTPUT_FILE = "emlakjet_details.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

session = requests.Session()
session.headers.update(HEADERS)

# Ensure output file exists
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# ---------------------------------------------
# Scrape details from a single property URL
# ---------------------------------------------
def scrape_property(url):
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        sel = html.fromstring(r.text)

        # Title
        title = sel.xpath('//h1[contains(@class,"styles_title")]//text()')
        title = " ".join(t.strip() for t in title if t.strip()) or None

        # Price
        price = sel.xpath('//span[contains(@class,"styles_price")]//text()')
        price = " ".join(t.strip() for t in price if t.strip()) or None

        # Images
        images = sel.xpath('//div[contains(@class,"styles_inner__")]//img/@src')
        images = list({img for img in images if img})

        return {"url": url, "title": title, "price": price, "images": images, "success": True}

    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return {"url": url, "title": None, "price": None, "images": [], "success": False, "error": str(e)}

# ---------------------------------------------
# Append single result to JSON file
# ---------------------------------------------
def save_one(result):
    with open(OUTPUT_FILE, "r+", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
        data.append(result)
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()

# ---------------------------------------------
# MAIN
# ---------------------------------------------
def main():
    # Load URLs
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Flatten all URLs
    all_urls = []
    for item in data:
        if "product_urls" in item and item["product_urls"]:
            all_urls.extend(item["product_urls"])
        if "sub_sub_category" in item and "product_urls" in item and item["product_urls"]:
            all_urls.extend(item["product_urls"])

    all_urls = list(set(all_urls))[:1000]  # first 1000 for testing

    success = 0
    failure = 0

    for idx, url in enumerate(all_urls, start=1):
        print(f"[{idx}/{len(all_urls)}] Scraping {url}")
        res = scrape_property(url)
        save_one(res)

        if res["success"]:
            success += 1
        else:
            failure += 1

        time.sleep(1)  # polite delay

    # Summary
    total_requests = success + failure
    print("\n-------- SUMMARY --------")
    print("Total Requests:", total_requests)
    print("Success:", success)
    print("Failure:", failure)
    if total_requests:
        print(f"Success Rate: {success / total_requests * 100:.2f}%")
    print(f"\nSaved results incrementally to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
