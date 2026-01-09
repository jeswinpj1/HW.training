import requests
import json
import time

# ----------------- CONFIG -----------------
BASE_SEARCH_URL = "https://www.jiomart.com/trex/search"
OUTPUT_FILE = "01_jiomart_tea_coffee_products.json"

cookies = {
    "nms_mgo_pincode": "600056",
    "nms_mgo_city": "Kanchipuram",
    "nms_mgo_state_code": "TN",
    "AKA_A2": "A",
}

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "origin": "https://www.jiomart.com",
    "referer": "https://www.jiomart.com/c/groceries/biscuits-drinks-packaged-foods/tea-coffee/29009",
    "x-requested-with": "XMLHttpRequest",
    "pin": "600056",
    "location_details": (
        '{"city":"Kanchipuram","state_code":"TN",'
        '"store_code":{"GROCERIES":{"3P":["groceries_zone_non-essential_services",'
        '"general_zone","groceries_zone_essential_services"],"1P":["2862"]}},'
        '"region_code":{"GROCERIES":["T1IP","PANINDIAGROCERIES"]},'
        '"vertical_code":["GROCERIES"]}'
    ),
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    ),
}

# Initial POST payload for Tea & Coffee category
json_data = {
    "pageSize": 50,
    "facetSpecs": [],
    "variantRollupKeys": ["variantId"],
    "branch": "projects/sr-project-jiomart-jfront-prod/locations/global/catalogs/default_catalog/branches/0",
    "pageCategories": ["29009"],  # Tea & Coffee category
    "userInfo": {"userId": None},
    "pageToken": "",
    "orderBy": "attributes.popularity desc",
    "filter": (
        'attributes.status:ANY("active") AND attributes.category_ids:ANY("29009") AND '
        '(attributes.available_regions:ANY("TXCF", "PANINDIAGROCERIES")) AND '
        '(attributes.inv_stores_1p:ANY("ALL", "T7GZ") OR '
        'attributes.inv_stores_3p:ANY("ALL", "groceries_zone_non-essential_services", '
        '"general_zone","groceries_zone_essential_services"))'
    ),
    "visitorId": "anonymous-16b88074-4641-4f8e-b5f9-c4e9141e3536",
}

# ----------------- INITIALIZE OUTPUT -----------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("[\n")  # start JSON array

first_product = True
page = 1
total_products = 0

# ----------------- PAGINATION LOOP -----------------
while True:
    print(f"Fetching page {page}...")
    response = requests.post(BASE_SEARCH_URL, headers=headers, cookies=cookies, json=json_data)

    if response.status_code != 200:
        print("Request failed:", response.status_code)
        break

    data = response.json()
    products = data.get("results", [])

    if not products:
        print("No more products found, stopping.")
        break

    for product in products:
        variants = product.get("product", {}).get("variants", [])
        for variant in variants:
            product_info = {
            "unique_id": variants[0].get("id") if variants else None,
            "retailer_name": "jiomart",
            "extraction_date": time.strftime("%Y-%m-%d"),
            "product_name": product.get("product", {}).get("title"),
            "brand": variants[0].get("brands", [""])[0] if variants else None,
            "url": variants[0].get("uri") if variants else None,
            "food_type" : variants[0].get("attributes", {}).get("food_type").get("text") if variants else None,
        }


            # Append product to file immediately
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                if not first_product:
                    f.write(",\n")
                json.dump(product_info, f, ensure_ascii=False, indent=2)
                first_product = False

            total_products += 1

    print(f"Collected {total_products} products so far.")

    # ----------------- NEXT PAGE -----------------
    next_page_token = data.get("nextPageToken")
    if not next_page_token:
        print("Reached last page.")
        break

    json_data["pageToken"] = next_page_token
    page += 1
    time.sleep(1)  # be polite with server

# ----------------- CLOSE JSON ARRAY -----------------
with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
    f.write("\n]")
print(f"Scraping completed. Total products fetched: {total_products}")




