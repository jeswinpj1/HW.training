
import requests
import json
import time

# Base API format for categories
CATEGORY_API_TEMPLATE = (
    "https://www.lidl.co.uk/q/api/search?"
    "offset={offset}&fetchsize=12&locale=en_GB&assortment=GB&version=2.1.0&category.id={category_id}"
)

def test_category_api(category_id="10068374", paginate=False, fetch_size=12): # Fetch all pages Fetch all pages
    offset = 0

    while True:
        # Format API URL with category ID and offset
        url = CATEGORY_API_TEMPLATE.format(offset=offset, category_id=category_id)
        response = requests.get(url)
        data = response.json()

        items = data.get("items", [])
        total = data.get("numFound") or data.get("keywordResults", {}).get("num_items_found", 0)

        # Print sample data from first product if available
        if items:
            sample = items[0]
            grid = sample.get("gridbox", {}).get("data", {})
            print(" - Product ID:", sample.get("code"))
            print(" - Title:", grid.get("title"))
            print(" - Brand:", grid.get("brand"))
            print(" - Price:", grid.get("price", {}).get("price"))
            print(" - Currency:", grid.get("price", {}).get("currencySymbol"))
            print(" - Stock Availability:", grid.get("stockAvailability", {}).get("badgeInfo", {}).get("badges", [{}])[0].get("text", ""))
        else:
            print(" No products found.")
            break

        # Stop if only single page is requested
        if not paginate:
            break

        # Stop when no more products or last page reached
        if offset + fetch_size >= total:
            print("\n Reached last page.")
            break

        offset += fetch_size
        time.sleep(0.2)

# sample api = https://www.lidl.co.uk/q/api/search?offset=12&fetchsize=12&locale=en_GB&assortment=GB&version=2.1.0&category.id=10068374

#  3. Findings 

#  FINDINGS SUMMARY FOR LIDL API:")
#  Products accessible directly via API (no JavaScript needed)")
#  Pagination works using offset & fetchsize")
#  Brand, title, price, stock available in API response")
#  No authentication / API key required")
#  Some fields like description/specifications may not appear fully in API")
# Category IDs must be collected manually or via webpage crawler")
# No direct review API (Lidl doesn't show product reviews 









