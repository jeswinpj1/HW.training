# import requests
# import json
# import time

# # ------------------------------
# # Load categories
# # ------------------------------
# with open("/home/user/HW.training/hm_categories_all_levels.json", "r", encoding="utf-8") as f:
#     categories = json.load(f)

# # ------------------------------
# # Headers for GraphQL requests
# # ------------------------------
# HEADERS = {
#     'accept': 'application/json',
#     'content-type': 'application/json',
#     'magento-store-code': 'hm_uae_store',
#     'magento-store-view-code': 'are_en',
#     'magento-website-code': 'are',
#     'mesh_context': 'live',
#     'mesh_locale': 'en',
#     'mesh_market': 'ae',
#     'referer': 'https://ae.hm.com/en/',
#     'store': 'are_en',
#     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
#     'x-algolia-api-key': 'a2fdc9d456e5e714d8b654dfe1d8aed8',
#     'x-algolia-application-id': 'HGR051I5XN'
# }

# GRAPHQL_URL = "https://ae.hm.com/graphql"

# # ------------------------------
# # Fetch all products for a category URL (paginated)
# # ------------------------------
# def fetch_products(url_path):
#     all_products = []
#     page = 0

#     while True:
#         variables = {
#             "indexName1": "hm_prod_ae_product_list",
#             "params1": f"filters=(stock>0)&hitsPerPage=36&page={page}",
#             "urlKey1": url_path.replace("https://ae.hm.com/en/", ""),
#             "lang1": "en"
#         }

#         query = """<your same GraphQL query>"""

#         try:
#             response = requests.get(
#                 GRAPHQL_URL,
#                 headers=HEADERS,
#                 params={"query": query, "variables": json.dumps(variables)},
#                 timeout=10
#             )
#             data = response.json()  # this can be None
#         except json.JSONDecodeError:
#             print(f"❌ Invalid JSON for {url_path} page {page}, skipping...")
#             break
#         except Exception as e:
#             print(f"❌ Request failed for {url_path} page {page}: {e}")
#             break

#         # Ensure data is a dict before accessing
#         if not isinstance(data, dict):
#             print(f"⚠️ Unexpected response type for {url_path} page {page}: {type(data)}")
#             break

#         results = data.get("data", {}).get("getProductListingWithCategory", {}).get("results")
#         if not results or not isinstance(results, list) or len(results) == 0:
#             print(f"⚠️ No results for {url_path} page {page}")
#             break

#         hits = results[0].get("hits", [])
#         nb_hits = results[0].get("nbHits", 0)

#         if not hits:
#             print(f"⚠️ No products found for {url_path} page {page}")
#             break

#         all_products.extend(hits)

#         if (page + 1) * 36 >= nb_hits:
#             break

#         page += 1
#         time.sleep(0.5)

#     return all_products

# # ------------------------------
# # Recursive category + product extraction
# # ------------------------------
# def build_tree(category):
#     node = {
#         "id": category.get("id"),
#         "name": category.get("name"),
#         "url_path": category.get("url_path"),
#         "nav_url_path": category.get("nav_url_path"),
#         "full_path": category.get("full_path", ""),
#         "products": fetch_products(category.get("url_path", "")),
#         "children": []
#     }

#     for child in category.get("children", []):
#         node["children"].append(build_tree(child))

#     return node

# # ------------------------------
# # Build tree for all categories
# # ------------------------------
# output_tree = [build_tree(cat) for cat in categories]

# # ------------------------------
# # Save final JSON
# # ------------------------------
# with open("/home/user/HW.training/hm_products_tree.json", "w", encoding="utf-8") as f:
#     json.dump(output_tree, f, indent=4, ensure_ascii=False)

# print("✅ Done. All categories and products saved in hm_products_tree.json")


import requests
import json

GRAPHQL_URL = "https://ae.hm.com/graphql"

HEADERS ={
    "content-type": "application/json",
    "accept": "application/json",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64)"
}
QUERY = """
 ($indexName1: String!, $params1: String!, $urlKey1: String, $lang1: String) { getProductListingWithCategory( input: { requests: [{ indexName: $indexName1, params: $params1, urlKey: $urlKey1, lang: $lang1 }] } ) { results { hits { sku gtm { gtm_brand gtm_cart_value gtm_category gtm_department_id gtm_department_name gtm_magento_product_id gtm_main_sku gtm_name gtm_old_price gtm_price gtm_product_sku gtm_product_style_code gtm_stock } in_stock discount { en } final_price { en } original_price { en } promotions { en } media { url image_type } media_pdp { url image_type } attr_color { en } attr_bv_rating_distribution { __typename } attr_bv_total_review_count attr_bv_average_overall_rating { en } title { en } url { en } attr_bv_rating { en } attr_product_collection { en } attr_product_brand { en } attr_collection_1 { en } attr_preview_preaccess_data { en } article_swatches { en { article_sku_code rgb_color } } swatches { en { child_sku_code rgb_color } } attr_color { en } attr_bv_rating { en } product_labels { en } member_price { ar en } catalogData { sku price { en } original_price { en } final_price { en } member_price { en { label name value roles } } promotions { en { label name value roles } } free_gift_promotion { en { label name value roles } } } } page hitsPerPage nbHits userData facets queryID _automaticInsights renderingContent params } } }
"""

def fetch_products(url_key):
    all_products = []
    page = 0

    while True:
        params = f"""
attributesToRetrieve=[
"url.en",
"attr_fragrance_name",
"attr_fragrance_category",
"attr_product_category.en",
"attr_product_collection.en",
"attr_form.en",
"attr_collection_1.en",
"attr_sub_title.en",
"media",
"media_pdp",
"title.en",
"article_swatches.en",
"promotions.en",
"product_labels.en",
"discount.en",
"original_price.en",
"final_price.en",
"attr_preview_preaccess_data.en",
"attr_bv_rating.en",
"attr_bv_total_review_count",
"attr_bv_average_overall_rating.en",
"product_labels.en",
"swatches.en",
"gtm",
"sku",
"attr_product_brand.en",
"attr_color.en",
"attr_brand_full_name.en",
"member_price",
"attr_size",
"field_acq_promotion_label.en.web"
]
&responseFields=[
"userData",
"facets",
"renderingContent",
"hits",
"nbHits",
"page",
"hitsPerPage",
"params"
]
&clickAnalytics=true
&facets=["*"]
&filters=(stock > 0)
&hitsPerPage=36
&optionalFilters=null
&page={page}
&userToken=anonymous-af401550-bb39-4853-bf4d-e908191d7c24
""".replace("\n", "")
        variables = {
            "indexName1": "hm_prod_ae_product_list",
            "params1": params,
            "urlKey1": url_key,
            "lang1": "en"
        }

        response = requests.post(
            GRAPHQL_URL,
            headers=HEADERS,
            json={"query": QUERY, "variables": variables},
            timeout=20
        )

        data = response.json()

        # error handler
        errors = data.get("errors")
        if errors:
            print(" GraphQL error:", errors)
            break

        results = (
            data.get("data", {})
                .get("getProductListingWithCategory", {})
                .get("results", [])
        )

        if not results:
            break

        hits = results[0].get("hits", [])

        if not hits:
            break

        print(f"Fetched page {page}: {len(hits)} products")
        all_products.extend(hits)

        # Pagination
        total = results[0].get("nbHits", 0)
        per_page = results[0].get("hitsPerPage", 36)

        if (page + 1) * per_page >= total:
            break

        page += 1

    return all_products


# ------------------------------
# Example: fetch products from "shop-men/new-arrivals"
# ------------------------------

products = fetch_products(url_key="shop-men/new-arrivals")


print(f" Total products fetched: {len(products)}")

# Save to JSON
with open("hm_products.json", "w", encoding="utf-8") as f:
    json.dump(products, f, indent=4, ensure_ascii=False)

print(" Saved product details to hm_products.json")





