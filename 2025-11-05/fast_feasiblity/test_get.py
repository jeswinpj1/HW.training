
import requests
import json
from urllib.parse import quote
import time

# --- Session & Headers ---
session = requests.Session()

headers = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "referer": "https://www.fastenal.com/product/all",
    "origin": "https://www.fastenal.com",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "x-xsrf-token": "YOUR_XSRF_TOKEN_HERE",  # replace
}

cookies = {
    "XSRF-TOKEN": "YOUR_XSRF_TOKEN_HERE",
    "CJSESSIONID": "YOUR_SESSION_ID",
    "TSESSIONID": "YOUR_TSESSION_ID",
}

category_menu_url = "https://www.fastenal.com/container/api/product-search/category-menu"
product_search_url = "https://www.fastenal.com/catalog/api/product-search"

# --- Step 1: Fetch main categories ---
resp = session.get(category_menu_url, headers=headers, cookies=cookies)
resp.raise_for_status()
category_data = resp.json()

# --- Step 2: Build tree (Level 1 → Level 2 → Level 3) ---
full_tree = []

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
    r2.raise_for_status()
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

# --- Step 3: Print tree ---
for main in full_tree:
    print(f"Main: {main['categoryLevelOne']} ({main['categoryId']})")
    for sub in main["subcategories"]:
        print(f"  Sub: {sub['categoryLevelTwo']} ({sub['categoryId']})")
        for sub3 in sub["subcategories"]:
            print(f"    SubSub: {sub3['categoryLevelThree']} ({sub3['categoryId']})")

# --- Optional: save JSON ---
with open("fastenal_category_tree_level3.json", "w", encoding="utf-8") as f:
    json.dump(full_tree, f, indent=2, ensure_ascii=False)

print(" Category tree (up to Level 3) created successfully!")
