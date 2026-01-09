

# import requests
# import json
# import re

# headers = {
#     'accept': 'application/json',
#     'accept-language': 'en-GB,en;q=0.9',
#     'cache-control': 'no-cache',
#     'content-type': 'application/json',
#     'magento-store-code': 'hm_uae_store',
#     'magento-store-view-code': 'are_en',
#     'magento-website-code': 'are',
#     'mesh_context': 'live',
#     'mesh_locale': 'en',
#     'mesh_market': 'ae',
#     'pragma': 'no-cache',
#     'priority': 'u=1, i',
#     'referer': 'https://ae.hm.com/en/',
#     'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Linux"',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'same-origin',
#     'store': 'are_en',
#     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
# }

# params = {
#     'query': 'query ($categoryId: String) { commerce_categories( filters: { ids: { eq: $categoryId } } include_in_menu: 1 ) { items { error { code message } id name level url_path nav_url_path image promo_id banners style_class show_in_tab direct_link position prev_prea_enabled preview_sd preview_ed preview_category_text preview_pdp_text preview_tier_type preview_timer preaccess_sd preaccess_ed preaccess_category_text preaccess_pdp_text preaccess_tier_type include_in_menu display_view_all gtm_name breadcrumbs { category_level category_name category_uid category_url_key category_url_path } children { id name level image url_path nav_url_path promo_id banners style_class show_in_tab direct_link position include_in_menu display_view_all gtm_name children { id name level image url_path nav_url_path promo_id banners style_class show_in_tab direct_link position include_in_menu display_view_all gtm_name children { id name level image url_path nav_url_path promo_id banners style_class show_in_tab direct_link position include_in_menu display_view_all gtm_name children { id name level image url_path nav_url_path promo_id banners style_class show_in_tab direct_link position include_in_menu display_view_all gtm_name children { id name level image url_path nav_url_path promo_id banners style_class show_in_tab direct_link position include_in_menu display_view_all gtm_name } } } } } } } }',
#     'variables': '{"categoryId":"2"}',
# }

# # ---------------- Safe JSON Loader ----------------
# def safe_json(raw):
#     raw = raw.strip()

#     if raw.startswith("<"):
#         raise ValueError("Received HTML block page, not JSON.")

#     # remove Akamai/Cloudflare prefixes if any exist
#     raw = re.sub(r"^\)\]\}',?\s*", "", raw)

#     match = re.search(r'\{.*\}', raw, flags=re.S)
#     if not match:
#         raise ValueError("No valid JSON found.")

#     return json.loads(match.group(0))


# # ---------------- Make Request ----------------
# print("Fetching category data…")

# response = requests.get(
#     'https://ae.hm.com/graphql',
#     params=params,
#     headers=headers,
# )

# print("Status:", response.status_code)

# try:
#     data = safe_json(response.text)
# except Exception as e:
#     print("❌ Failed to parse JSON:", e)
#     print("RAW RESPONSE:")
#     print(response.text[:500])
#     raise SystemExit

# # ---------------- Save JSON ----------------
# output_file = "hm_categories.json"

# with open(output_file, "w", encoding="utf-8") as f:
#     json.dump(data, f, ensure_ascii=False, indent=2)

# print(f"✅ Saved category tree to {output_file}")



import requests
import json

# ------------------------------
# HEADERS
# ------------------------------
headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'magento-store-code': 'hm_uae_store',
    'magento-store-view-code': 'are_en',
    'magento-website-code': 'are',
    'mesh_context': 'live',
    'mesh_locale': 'en',
    'mesh_market': 'ae',
    'referer': 'https://ae.hm.com/en/',
    'store': 'are_en',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0'
}

# ------------------------------
# PARAMS (GraphQL query)
# ------------------------------
params = {
    "query": """
        query ($categoryId: String) {
            commerce_categories(
                filters: { ids: { eq: $categoryId } }
                include_in_menu: 1
            ) {
                items {
                    id
                    name
                    url_path
                    nav_url_path
                    children {
                        id
                        name
                        url_path
                        nav_url_path
                        children {
                            id
                            name
                            url_path
                            nav_url_path
                            children {
                                id
                                name
                                url_path
                                nav_url_path
                                children {
                                    id
                                    name
                                    url_path
                                    nav_url_path
                                }
                            }
                        }
                    }
                }
            }
        }
    """,
    "variables": '{"categoryId":"2"}'
}

# ------------------------------
# FETCH RESPONSE
# ------------------------------
response = requests.get("https://ae.hm.com/graphql", params=params, headers=headers)
raw_json = response.json()

# ------------------------------
# RECURSIVE EXTRACTION WITH FULL PATH
# ------------------------------
output = []

def extract_recursive(item, parent_path=None):
    if parent_path is None:
        parent_path = []

    # Build current full path
    current_path = parent_path + [item.get("name") or ""]

    output.append({
        "id": item.get("id"),
        "name": item.get("name"),
        "url_path": item.get("url_path") or "",
        "nav_url_path": item.get("nav_url_path") or "",
        "full_path": " > ".join(current_path)
    })

    # Recursively extract children
    for child in item.get("children", []):
        extract_recursive(child, current_path)

# Start extraction
items = raw_json.get("data", {}).get("commerce_categories", {}).get("items", [])
for item in items:
    extract_recursive(item)

# ------------------------------
# SAVE JSON OUTPUT
# ------------------------------
with open("hm_categories_all_levels.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("✅ Extracted categories:", len(output))
print("💾 Saved to hm_categories_all_levels.json")
