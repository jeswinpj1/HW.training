import requests
import json
import re
import time

INPUT_FILE = "navigation_api_urls.txt"
OUTPUT_FILE = "lidl_products_flat.jsonl"

def map_product(product):
    grid = product.get("gridbox", {}).get("data", {})
    price = grid.get("price", {})

    return {
        "unique_id": str(product.get("code", "")),
        "brand": grid.get("brand", ""),
        "category": grid.get("category", ""),
        "product_type": grid.get("productType", ""),
        "description": grid.get("keyfacts", {}).get("description", ""),
        "competitor_name": "Lidl",
        "stockAvailability": grid.get("stockAvailability", {}).get("badgeInfo", {}).get("badges", [{}])[0].get("text", ""),
        "productId": grid.get("productId", ""),
        "product_url": "https://www.lidl.co.uk" + grid.get("canonicalUrl", ""),
        "currency": price.get("currencySymbol", ""),
        "price": price.get("price", ""),
        "title": grid.get("title", ""),
    }

def fetch_products(api_url, outfile):
    offset = 0
    fetch_size = 12

    while True:
        paginated_url = re.sub(r"offset=\d+", f"offset={offset}", api_url)

        try:
            response = requests.get(paginated_url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f" Error fetching {paginated_url}: {e}")
            break

        items = data.get("items", [])
        num_found = data.get("numFound") or data.get("keywordResults", {}).get("num_items_found", 0)

        if not items:
            break

        for product in items:
            outfile.write(json.dumps(map_product(product), ensure_ascii=False) + "\n")

        print(f" Offset {offset} fetched ({len(items)} products)")
        offset += fetch_size

        if offset >= num_found:
            break

        time.sleep(0.1)

def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        with open(INPUT_FILE, "r", encoding="utf-8") as infile:
            for url in infile:
                url = url.strip()
                if url:
                    print(f"\n Fetching category: {url}")
                    fetch_products(url, out)

    print(f"\n Done! Products saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()





