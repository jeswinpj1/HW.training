

# from curl_cffi import requests
# from parsel import Selector
# import requests
# import json

# URL = "https://www.homedepot.ca/product/energizer-energizer-max-aa-batteries-36-pack-double-a-alkaline-batteries/1000184321"

# headers = {
#     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#     'accept-language': 'en-US,en;q=0.9',
#     'cache-control': 'max-age=0',
#     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
# }

# # Send request
# response = requests.get(URL, headers=headers, timeout=20)

# # Parse HTML
# sel = Selector(response.text)

# # Extract JSON from <script id="hdca-state">
# script_json = sel.xpath("//script[@id='hdca-state']/text()").get()

# if not script_json:
#     raise ValueError("No hdca-state script found")

# data = json.loads(script_json)

# # There is usually only one key (product ID)
# product_id = list(data.keys())[0]
# product = data[product_id]["b"]

# # Extract details
# product_name = product.get("name")
# manufacturer = product.get("manufacturer")
# model_number = product.get("modelNumber")
# price = product.get("price", {}).get("formattedValue")
# currency = product.get("price", {}).get("currencyIso")
# description = product.get("description")
# number_of_reviews = product.get("numberOfReviews")
# average_rating = product.get("averageRating")
# images = [img.get("url") for img in product.get("images", [])]
# alternate_images = [img.get("url") for img in product.get("alternateImages", [])]
# categories = [cat.get("name") for cat in product.get("categories", [])]

# # Dimensions & weight
# item_width = product.get("itemWidth")
# item_height = product.get("itemHeight")
# item_depth = product.get("itemDepth")
# item_weight = product.get("itemWeight")

# # Print result
# print("Product Name:", product_name)
# print("Manufacturer:", manufacturer)
# print("Model Number:", model_number)
# print("Price:", price, currency)
# print("Description:", description)
# print("Reviews:", number_of_reviews, "Average Rating:", average_rating)
# print("Categories:", categories)
# print("Images:", images)
# print("Alternate Images:", alternate_images)
# print("Dimensions (WxHxD):", item_width, "x", item_height, "x", item_depth)
# print("Weight:", item_weight)




from curl_cffi import requests
from parsel import Selector
import json

URL = "https://www.homedepot.ca/product/energizer-energizer-max-aa-batteries-36-pack-double-a-alkaline-batteries/1000184321"

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
}

success = 0
fail = 0

for i in range(1, 1001):  # ✅ test 100 requests
    try:
        response = requests.get(URL, headers=headers, impersonate="chrome", timeout=20)
        print(f"Request {i}: Status {response.status_code}")

        sel = Selector(response.text)

        # Extract JSON from <script id="hdca-state">
        script_json = sel.xpath("//script[@id='hdca-state']/text()").get()
        if not script_json:
            print("  ➤ hdca-state script NOT found")
            fail += 1
            continue

        data = json.loads(script_json)
        product_id = list(data.keys())[0]
        product = data[product_id]["b"]

        product_name = product.get("name")
        price = product.get("price", {}).get("formattedValue")
        currency = product.get("price", {}).get("currencyIso")

        if product_name and price:
            print(f"  ➤ Name: {product_name.strip()}, Price: {price} {currency}")
            success += 1
        else:
            print("  ➤ Product details NOT found")
            fail += 1

    except Exception as e:
        print(f"  ➤ Exception: {e}")
        fail += 1

# Summary
total = success + fail
success_pct = round((success / total) * 100, 2)
fail_pct = round((fail / total) * 100, 2)

print("\n==== SUMMARY ====")
print("Total Requests:", total)
print("Success:", success, f"({success_pct}%)")
print("Failure:", fail, f"({fail_pct}%)")
