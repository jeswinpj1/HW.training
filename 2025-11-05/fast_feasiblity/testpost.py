import json
import requests
from time import sleep

# Load your products JSON
with open("/home/user/HW.training/fastenal_products_paginated.json") as f:
    products = [json.loads(line) for line in f]

# API details
API_URL = "https://www.fastenal.com/catalog/api/product-search"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "x-xsrf-token": "ec06c18c-b6ea-45bc-a9a6-c102802de61c"
}
COOKIES = {
    "XSRF-TOKEN": "ec06c18c-b6ea-45bc-a9a6-c102802de61c",
    # add any other necessary cookies here
}

results = []

for product in products[:3]:

    sku = product["sku"]
    payload = {
        "sku": [sku],
        "productDetails": True,
        "attributeFilters": {},
        "pageUrl": f"/product/details/{sku}"
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, cookies=COOKIES, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract the details you want
        product_details = data.get("productDetail", {})  # usually a list with one product
        product["UPC"] = product_details.get("unspscCode", "")
        product["Model Number"] = product_details.get("modelNumber", "")
        product["Manufacturer Part Number"] = product_details.get("manufacturerPartNumber", "")
        product["Full Product Description"] = product_details.get("notes", {}).get("mp_bulletPoints", "")

        results.append(product)
        print(f" Fetched details for SKU {sku}")

    except Exception as e:
        print(f" Failed for SKU {sku}: {e}")

    sleep(0.5)  # polite delay

# Save updated products
with open("fastenal_products_with_details.json", "w") as f:
    for item in results:
        f.write(json.dumps(item) + "\n")
