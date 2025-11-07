import requests
import json
import time
from urllib.parse import quote

# ======================================
# CONFIGURATION
# ======================================
API_CATEGORY = "https://www.fastenal.com/container/api/product-search/category-menu"
API_SEARCH = "https://www.fastenal.com/catalog/api/product-search"

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
# CATEGORY API GENRATION 
# ======================================
ull_tree = []
for main_cat in category_data.get("categoryList", []):
    main_id = main_cat.get("categoryId")
    main_name = main_cat.get("categoryLevelOne")
    page_url_main = f"/product/{quote(main_name)}"
    main_entry = {
        "categoryId": main_id,
        "categoryLevelOne": main_name,
        "subcategories": []
    }
    # Fetch Level 2 subcategories
    payload_level2 = {
        "categoryLevelOne": main_name,
        "categoryId": main_id,
        "ignoreCounterBook": True,
        "attributeFilters": {},
        "pageUrl": page_url_main
    }
    r2 = session.post(product_search_url, headers=headers, cookies=cookies, json=payload_level2)
    data_level2 = r2.json()
    level2_list = data_level2.get("categoryList", [])

    for sub in level2_list:
        level2_id = sub.get("categoryId")
        level2_name = sub.get("categoryLevelTwo")
        page_url_sub = f"/product/{quote(main_name)}/{quote(level2_name)}"

        sub_entry = {
            "categoryId": level2_id,
            "categoryLevelOne": main_name,
            "categoryLevelTwo": level2_name,
            "subcategories": []
        }

        # Fetch Level 3 subcategories for this Level 2
        payload_level3 = {
            "categoryLevelOne": main_name,
            "categoryLevelTwo": level2_name,
            "categoryId": level2_id,
            "ignoreCounterBook": True,
            "attributeFilters": {},
            "pageUrl": page_url_sub
        }

        r3 = session.post(product_search_url, headers=headers, cookies=cookies, json=payload_level3)
        r3.raise_for_status()
        data_level3 = r3.json()
        level3_list = data_level3.get("categoryList", [])

        for sub3 in level3_list:
            sub3_entry = {
                "categoryId": sub3.get("categoryId"),
                "categoryLevelOne": main_name,
                "categoryLevelTwo": level2_name,
                "categoryLevelThree": sub3.get("categoryLevelThree")
            }
            sub_entry["subcategories"].append(sub3_entry)

        main_entry["subcategories"].append(sub_entry)
        time.sleep(0.2)

    full_tree.append(main_entry)
    time.sleep(0.3)
# ======================================
# CRAWL PRODUCTS & DETAILS
# ======================================
for main in category_tree:
    lvl1 = main.get("categoryLevelOne")
    for sub in main.get("subcategories", []):
        lvl2 = sub.get("categoryLevelTwo")
        for sub3 in sub.get("subcategories", []):
            lvl3 = sub3.get("categoryLevelThree")
            category_id = sub3.get("categoryId")
            if not lvl3 or not category_id:
                continue
            page_url = f"/product/{quote(lvl1)}/{quote(lvl2)}/{quote(lvl3)}"          
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
                    r = session.post(API_SEARCH, headers=headers, cookies=cookies, json=payload, timeout=30)      
                    data = r.json()
                    total_pages = data.get("paging", {}).get("totalPages", 1)
                    product_list = data.get("productList", [])
                    records = []
                    for product in product_list:
                        sku = product.get("sku")
                        details = fetch_product_details(sku)
                        records.append({
                            "SKU": sku,
                            "Company Name": product.get("brNm", "FASTENAL"),
                            "Manufacturer Name": product.get("mfr", ""),
                            "Brand Name": product.get("mp_brLbl") or product.get("mp_mLbl") or "",
                            "Vendor/Seller Part Number": sku,
                            "Item Name": product.get("mp_des", ""),
                            "Price": next((p.get("pr") for p in product.get("pdd", []) if p.get("dataName")=="Online Price:"), ""),
                            "Unit of Issue": next((p.get("mp_uom") for p in product.get("pdd", []) if p.get("dataName")=="Online Price:"), ""),
                            "Availability": product.get("productEda", {}).get("mp_availabilityMessage", ""),
                            "Full Product Description": details.get("Full Product Description", ""),
                            "pdp_url": f"https://www.fastenal.com/product/details/{sku}"
                        })
                    page += 1
                    time.sleep(0.5)
# ======================================
# PARSER FUNCTIONS
# ======================================
    payload = {"sku": [sku], "productDetails": True, "attributeFilters": {}, "pageUrl": f"/product/details/{sku}"}
    try:
        r = session.post(API_SEARCH, headers=headers, cookies=cookies, json=payload, timeout=30)
        data = r.json()
        detail = data.get("productDetail", {})
        return {
            "UPC": detail.get("unspscCode", ""),
            "Model Number": detail.get("modelNumber", ""),
            "Manufacturer Part Number": detail.get("manufacturerPartNumber", ""),
            "Full Product Description": detail.get("notes", {}).get("mp_bulletPoints", "")
        }
    