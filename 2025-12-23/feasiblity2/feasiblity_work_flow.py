import requests
from parsel import Selector
from urllib.parse import urljoin

url = "https://eu.targus.com"
"

response = requests.get(url, timeout=30)
print("Status:", response.status_code)

sel = Selector(response.text)

# extract hrefs
urls = sel.xpath('//a[@class="grandchildlink"]/@href').getall()

def extract_category_id(url):
    """Extract category_id from a saved URL query or path"""
    # if your URLs already contain category_id in query params, extract it
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if "category_id" in qs:
        return qs["category_id"][0]
    # fallback: try to extract from URL path numbers
    parts = parsed.path.strip("/").split("-")
    for p in parts:
        if p.isdigit():
            return p
    return None

def fetch_products(category_id):
    """Fetch all products for a category using pagination"""
    page_num = 1
    while True:
        api_url = (
            f"https://api.fastsimon.com/categories_navigation"
            f"?request_source=v-next&src=v-next&UUID=8fb07dc3-f0b7-4ea1-bc29-4286c08e8c3f"
            f"&uuid=8fb07dc3-f0b7-4ea1-bc29-4286c08e8c3f&store_id={STORE_ID}"
            f"&api_type=json&category_id={category_id}&facets_required=1"
            f"&products_per_page={PRODUCTS_PER_PAGE}&page_num={page_num}&with_product_attributes=true&qs=false"
        )

        resp = requests.get(api_url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print(f"[ERROR] Failed to fetch page {page_num} for category {category_id}")
            break

        data = resp.json()
        items = data.get("items", [])
        if not items:
            break  # no more products

        for item in items:
            save_product(item)

        print(f"Saved {len(items)} products from page {page_num} (category {category_id})")
        page_num += 1
        time.sleep(0.5)  # be polite