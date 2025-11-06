import requests
import json
import time
from urllib.parse import quote

# ======================================
# CONFIGURATION
# ======================================
TREE_FILE = "/home/user/HW.training/fastenal_category_tree_level3.json"  # ← from your category extraction script
OUTPUT_FILE = "fastenal_products_paginated.json"
API_URL = "https://www.fastenal.com/catalog/api/product-search"

# ======================================
# HEADERS & COOKIES
# ======================================
headers = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://www.fastenal.com",
    "referer": "https://www.fastenal.com/product/all",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ),
    "x-xsrf-token": "4f05ca58-d4f9-4d34-95ec-dc601b786451"
}

cookies = {
    "XSRF-TOKEN": "4f05ca58-d4f9-4d34-95ec-dc601b786451",
    "CJSESSIONID": "ZGQ0ZWMyZDItYTQ2Mi00MjdlLWE5NDctN2FjYmMxMTgzMTJm",
    "TSESSIONID": "NmVmYjYxMmMtODBjYy00ZDk0LWE4MTItMjQzODBmYTkyNGM0"
}

session = requests.Session()

# ======================================
# LOAD CATEGORY TREE
# ======================================
with open(TREE_FILE, "r", encoding="utf-8") as f:
    category_tree = json.load(f)

def save_page_data(records):
    """Append one page of products to output JSONL file."""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
# ======================================
# CRAWL PRODUCTS (WITH PAGINATION)
# ======================================
all_products = []

for main in category_tree:
    lvl1 = main.get("categoryLevelOne")

    for sub in main.get("subcategories", []):
        lvl2 = sub.get("categoryLevelTwo")

        for sub3 in sub.get("subcategories", []):
            lvl3 = sub3.get("categoryLevelThree")
            category_id = sub3.get("categoryId")
            if not lvl3 or not category_id:
                continue

            # --- Construct page URL ---
            page_url = f"/product/{quote(lvl1)}/{quote(lvl2)}/{quote(lvl3)}"

            print(f"\n🔹 Processing category: {lvl1} > {lvl2} > {lvl3} ({category_id})")

            page = 1
            total_pages = 1

            while page <= total_pages:
                payload = {
                    "categoryLevelOne": lvl1,
                    "categoryLevelTwo": lvl2,
                    "categoryLevelThree": lvl3,
                    "ignoreCounterBook": True,
                    "categoryId": category_id,
                    "productListOnly": "true",
                    "attributeFilters": {},
                    "pageUrl": page_url,
                    "page": page
                }

                try:
                    response = session.post(API_URL, headers=headers, cookies=cookies, json=payload, timeout=30)
                    if response.status_code == 403:
                        print("❌ 403 Forbidden: check token/session.")
                        break
                    response.raise_for_status()

                    data = response.json()

                    # --- Get total pages ---
                    pagination = data.get("paging", {})
                    total_pages = pagination.get("totalPages", 1)

                    # --- Extract product SKUs ---
                    product_list = data.get("productList", [])
                    page_records = []

                    for product in product_list:
                        sku = product.get("sku")
                        company_name = product.get("brNm", "FASTENAL")
                        manufacturer_name = product.get("mfr", "")
                        brand_name = product.get("mp_brLbl") or product.get("mp_mLbl") or ""
                        vendor_seller_part_number = product.get("sku", "")
                        item_name = product.get("mp_des", "")
                        manufacturer_part_no = product.get("manufacturerPartNo", "")
                        country_of_origin = product.get("acceptableCountryOfOrigin", "")
                        upc = product.get("unspscCode", "")
                        model_number = product.get("manufacturerPartNo", "")

                        # Full Product Description
                        full_description = " ".join(
                            filter(None, [
                                product.get("mp_bulletPoints"),
                                product.get("mp_publicNotes"),
                                product.get("mp_applicationUse")
                            ])
                        )

                        # Price & Unit of Issue
                        price, unit_of_issue = "", ""
                        for p in product.get("pdd", []):
                            if p.get("dataName") == "Online Price:":
                                price = p.get("pr", "")
                                unit_of_issue = p.get("mp_uom", "")
                                break

                        qty_per_uoi = product.get("uom", {}).get("mp_msg", "")
                        availability = product.get("productEda", {}).get("mp_availabilityMessage", "")

                        # --- Assemble record ---
                        page_records.append({
                            "categoryLevelOne": lvl1,
                            "categoryLevelTwo": lvl2,
                            "categoryLevelThree": lvl3,
                            "categoryId": category_id,
                            "page": page,
                            "sku": sku,
                            "Company Name": company_name,
                            "Manufacturer Name": manufacturer_name,
                            "Brand Name": brand_name,
                            "Vendor/Seller Part Number": vendor_seller_part_number,
                            "Item Name": item_name,
                            "Full Product Description": full_description,
                            "Price": price,
                            "Unit of Issue": unit_of_issue,
                            "QTY Per UOI": qty_per_uoi,
                            "Product Category": f"{lvl1} / {lvl2} / {lvl3}",
                            "Availability": availability,
                            "Manufacturer Part Number": manufacturer_part_no,
                            "Country of Origin": country_of_origin,
                            "UPC": upc,
                            "Model Number": model_number,
                            "pdp_url":"https://www.fastenal.com/product/details/" + str(sku)
                        })
                    if page_records:
                        save_page_data(page_records)
                        
                    print(f" Page {page}/{total_pages} | Found {len(product_list)} products")

                    page += 1
                    time.sleep(0.5)

                except Exception as e:
                    print(f" Error on {lvl3} (page {page}): {e}")
                    break

# ======================================
# SAVE RESULTS
# ======================================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_products, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done! Total products: {len(all_products)}")
print(f"Saved to: {OUTPUT_FILE}")












# import requests
# import json
# import time
# from urllib.parse import quote

# # ======================================
# # CONFIGURATION
# # ======================================
# TREE_FILE = "/home/user/HW.training/fastenal_category_tree_level3.json"  # ← from your category extraction script
# OUTPUT_FILE = "fastenal_products_paginated.json"
# API_URL = "https://www.fastenal.com/catalog/api/product-search"

# # ======================================
# # HEADERS & COOKIES
# # ======================================
# headers = {
#     "accept": "application/json, text/plain, */*",
#     "content-type": "application/json",
#     "origin": "https://www.fastenal.com",
#     "referer": "https://www.fastenal.com/product/all",
#     "user-agent": (
#         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
#         "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
#     ),
#     "x-xsrf-token": "4f05ca58-d4f9-4d34-95ec-dc601b786451"
# }

# cookies = {
#     "XSRF-TOKEN": "4f05ca58-d4f9-4d34-95ec-dc601b786451",
#     "CJSESSIONID": "ZGQ0ZWMyZDItYTQ2Mi00MjdlLWE5NDctN2FjYmMxMTgzMTJm",
#     "TSESSIONID": "NmVmYjYxMmMtODBjYy00ZDk0LWE4MTItMjQzODBmYTkyNGM0"
# }

# session = requests.Session()

# # ======================================
# # LOAD CATEGORY TREE
# # ======================================
# with open(TREE_FILE, "r", encoding="utf-8") as f:
#     category_tree = json.load(f)

# def save_page_data(records):
#     """Append one page of products to output JSONL file."""
#     with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
#         for r in records:
#             f.write(json.dumps(r, ensure_ascii=False) + "\n")
# # ======================================
# # CRAWL PRODUCTS (WITH PAGINATION)
# # ======================================
# all_products = []

# for main in category_tree:
#     lvl1 = main.get("categoryLevelOne")

#     for sub in main.get("subcategories", []):
#         lvl2 = sub.get("categoryLevelTwo")

#         for sub3 in sub.get("subcategories", []):
#             lvl3 = sub3.get("categoryLevelThree")
#             category_id = sub3.get("categoryId")
#             if not lvl3 or not category_id:
#                 continue

#             # --- Construct page URL ---
#             page_url = f"/product/{quote(lvl1)}/{quote(lvl2)}/{quote(lvl3)}"

#             print(f"\n🔹 Processing category: {lvl1} > {lvl2} > {lvl3} ({category_id})")

#             page = 1
#             total_pages = 1

#             while page <= total_pages:
#                 payload = {
#                     "categoryLevelOne": lvl1,
#                     "categoryLevelTwo": lvl2,
#                     "categoryLevelThree": lvl3,
#                     "ignoreCounterBook": True,
#                     "categoryId": category_id,
#                     "productListOnly": "true",
#                     "attributeFilters": {},
#                     "pageUrl": page_url,
#                     "page": page
#                 }

#                 try:
#                     response = session.post(API_URL, headers=headers, cookies=cookies, json=payload, timeout=30)
#                     if response.status_code == 403:
#                         print("❌ 403 Forbidden: check token/session.")
#                         break
#                     response.raise_for_status()

#                     data = response.json()

#                     # --- Get total pages ---
#                     pagination = data.get("paging", {})
#                     total_pages = pagination.get("totalPages", 1)

#                     # --- Extract product SKUs ---
#                     product_list = data.get("productList", [])
#                     page_records = []

#                     for product in product_list:
#                         sku = product.get("sku")
#                         if not sku:
#                             continue

#                         # --- Product detail API call ---
#                         pdp_url = f"https://www.fastenal.com/catalog/api/product-detail?sku={sku}"
#                         try:
#                             pdp_resp = session.get(pdp_url, headers=headers, cookies=cookies, timeout=20)
#                             pdp_resp.raise_for_status()
#                             pdp_data = pdp_resp.json().get("productDetail", {})

#                             # --- Map required fields ---
#                             company_name = pdp_data.get("brNm", "FASTENAL")
#                             manufacturer_name = pdp_data.get("mfr", "")
#                             brand_name = pdp_data.get("mp_brLbl") or pdp_data.get("mp_mLbl") or ""
#                             vendor_seller_part_number = pdp_data.get("sku", "")
#                             item_name = pdp_data.get("mp_des", "")
#                             manufacturer_part_no = pdp_data.get("manufacturerPartNo", "")
#                             country_of_origin = pdp_data.get("acceptableCountryOfOrigin", "")
#                             upc = pdp_data.get("unspscCode", "")
#                             model_number = pdp_data.get("manufacturerPartNo", "")

#                             # Full Product Description
#                             full_description = " ".join(
#                                 filter(None, [
#                                     pdp_data.get("mp_bulletPoints"),
#                                     pdp_data.get("mp_publicNotes"),
#                                     pdp_data.get("mp_applicationUse")
#                                 ])
#                             )

#                             # Price & Unit of Issue
#                             price, unit_of_issue = "", ""
#                             for p in pdp_data.get("pdd", []):
#                                 if p.get("dataName") == "Online Price:":
#                                     price = p.get("pr", "")
#                                     unit_of_issue = p.get("mp_uom", "")
#                                     break

#                             qty_per_uoi = pdp_data.get("uom", {}).get("mp_msg", "")
#                             availability = pdp_data.get("productEda", {}).get("mp_availabilityMessage", "")

#                             # --- Assemble record ---
#                             page_records.append({
#                                 "categoryLevelOne": lvl1,
#                                 "categoryLevelTwo": lvl2,
#                                 "categoryLevelThree": lvl3,
#                                 "categoryId": category_id,
#                                 "page": page,
#                                 "sku": sku,
#                                 "pdp_url": pdp_url,
#                                 "Company Name": company_name,
#                                 "Manufacturer Name": manufacturer_name,
#                                 "Brand Name": brand_name,
#                                 "Vendor/Seller Part Number": vendor_seller_part_number,
#                                 "Item Name": item_name,
#                                 "Full Product Description": full_description,
#                                 "Price": price,
#                                 "Unit of Issue": unit_of_issue,
#                                 "QTY Per UOI": qty_per_uoi,
#                                 "Product Category": f"{lvl1} / {lvl2} / {lvl3}",
#                                 "URL": f"https://www.fastenal.com/product/{sku}",
#                                 "Availability": availability,
#                                 "Manufacturer Part Number": manufacturer_part_no,
#                                 "Country of Origin": country_of_origin,
#                                 "UPC": upc,
#                                 "Model Number": model_number
#                             })

#                         except Exception as e:
#                             print(f"⚠️ Failed to fetch details for SKU {sku}: {e}")

#                     if page_records:
#                         save_page_data(page_records)

#                     print(f"✅ Page {page}/{total_pages} | Found {len(product_list)} products")
#                     page += 1
#                     time.sleep(0.5)

#                 except Exception as e:
#                     print(f"⚠️ Error on {lvl3} (page {page}): {e}")
#                     break


# # ======================================
# # SAVE RESULTS
# # ======================================
# with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#     json.dump(all_products, f, indent=2, ensure_ascii=False)

# print(f"\n✅ Done! Total products: {len(all_products)}")
# print(f"Saved to: {OUTPUT_FILE}")