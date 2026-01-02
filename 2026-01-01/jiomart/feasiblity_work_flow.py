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

#.......................................
# crawler 
#.......................................

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

#............................................................
# parser 
#............................................................


# ---------------- PDP HTML extraction ---------------- #
def extract_pdp_data(url, retries=3):
    for attempt in range(1, retries+1):
        try:
            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code != 200:
                print(f"[PDP] Failed ({res.status_code}) for {url}")
                return {}
            sel = Selector(text=res.text)

            breadcrumbs = " > ".join(
                sel.xpath('//li[@class="jm-breadcrumbs-list-item"]/a/text()').getall()
            ) or None

            specifications = {}
            rows = sel.xpath('//tr[@class="product-specifications-table-item"]')
            for row in rows:
                key = row.xpath('.//th/text()').get()
                value = row.xpath('.//td//text()').get()
                if key:
                    specifications[key.strip()] = value.strip() if value else None

            description = " ".join(sel.xpath('//div[@id="pdp_description"]//text()').getall()).strip() or None
            images = ",".join(sel.xpath('//img[@class="swiper-thumb-slides-img lazyload"]/@src').getall())

            return {
                "breadcrumbs": breadcrumbs,
                "specifications": specifications,
                "product_type": specifications.get("Product Type"),
                "item_form": specifications.get("Tea Form"),
                "flavour": specifications.get("Flavor"),
                "country_of_origin": specifications.get("Country of Origin"),
                "allergens": specifications.get("Allergens Included"),
                "ingredients": specifications.get("Ingredients"),
                "description": description,
                "images": images,
            }

        except requests.exceptions.ReadTimeout:
            print(f"[Timeout] PDP attempt {attempt} for {url}")
            time.sleep(5)
        except Exception as e:
            print(f"[ERROR] PDP {url}: {e}")
            return {}
    return {}

# ---------------- Price API extraction ---------------- #
def extract_price_data(unique_id):
    url = f"https://www.jiomart.com/catalog/productdetails/get/{unique_id}"
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            return {}
        data = res.json().get("data")
        if isinstance(data, list):
            data = data[0] if data else {}
        return {
            "regular_price": data.get("mrp"),
            "selling_price": data.get("selling_price"),
            "discount_percentage": data.get("discount_pct"),
        }
    except Exception as e:
        print(f"[ERROR] Price API {unique_id}: {e}")
        return {}

# ---------------- MAIN PIPELINE ---------------- #
all_variants = []
page_num = 1
total_products = 0

with open(OUTPUT_JL, "w", encoding="utf-8") as outfile:
    outfile.write("")  # create empty file

while True:
    print(f"Fetching page {page_num}...")
    try:
        response = requests.post(BASE_SEARCH_URL, headers=headers, cookies=cookies, json=json_data, timeout=30)
        if response.status_code != 200:
            print("Search request failed:", response.status_code)
            break

        data = response.json()
        results = data.get("results", [])
        if not results:
            print("No more results found, stopping.")
            break

        for product in results:
            prod_id = product.get("id")
            variants = product.get("variants", []) or product.get("product", {}).get("variants", [])
            for variant in variants:
                variant_id = variant.get("id")
                variant_name = variant.get("title") or product.get("product", {}).get("title")
                pdp_url = variant.get("uri") or product.get("product", {}).get("uri")

                enriched = {
                    "variant_id": variant_id,
                    "product_id": prod_id,
                    "product_name": variant_name,
                    "variant_name": variant_name,
                    "brand": variant.get("brands", [""])[0] if variant.get("brands") else None,
                    "size": variant.get("sizes", []),
                    "url": pdp_url,
                    "images": [img.get("uri") for img in variant.get("images", [])],
                }

                # Add PDP and Price Data
                enriched.update(extract_pdp_data(pdp_url))
                enriched.update(extract_price_data(variant_id))
                enriched["pdp_fetched_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

                # Save to JSONL immediately
                with open(OUTPUT_JL, "a", encoding="utf-8") as f:
                    f.write(json.dumps(enriched, ensure_ascii=False) + "\n")

                total_products += 1

        print(f"Collected {total_products} products so far.")

        # ----------------- NEXT PAGE -----------------
        next_token = data.get("nextPageToken")
        if not next_token:
            print("Reached last page.")
            break
        json_data["pageToken"] = next_token
        page_num += 1
        time.sleep(1)

    except requests.exceptions.ReadTimeout:
        print(f"[Timeout] Search page {page_num} retrying...")
        time.sleep(5)
        continue
    except Exception as e:
        print(f"[ERROR] Page {page_num}: {e}")
        break

print(f"Scraping completed. Total products fetched: {total_products}")

#.................................................................
# findings
#.................................................................
#only beverages(tea,coffee) category
#1. The API reports a total count of 3,576 products, but only 3,476 are extracted due to a pagination
#  limit encountered at the 71st page when no next-page token is available.