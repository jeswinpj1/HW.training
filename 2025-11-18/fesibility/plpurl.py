import json
import requests
from lxml import html
from time import sleep

# Load subcategories JSON
with open("subcats.json", "r", encoding="utf-8") as f:
    subcats = json.load(f)

# ----------------------------
# FIXED HEADERS / COOKIES (same as your curl)
# ----------------------------
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://2xlhome.com",
    "sec-ch-ua": "\"Chromium\";v=\"142\", \"Google Chrome\";v=\"142\", \"Not_A Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Linux\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

COOKIES = {
    "PHPSESSID": "7fc1779817d0b383b7cc5606712246d2",
    "form_key": "d34LJvkYZTYtL88X",
    "_ga": "GA1.1.1807385951.1758085159"
}

# ----------------------------
# API URL TEMPLATE (correct double p param)
# ----------------------------
API_TEMPLATE = (
    "https://2xlhome.com/ae-en/{slug}?p={page}&p={page}"
    "&_category_id={subcat_id}"
    "&_core_filters=W10%3D"
    "&_sections=product_list"
    "&isPowerListingAjax=b6bdd9ecd08caf7084a957e7d3e2126b"
)

# Output structure
output = {}

# -------------------------------------------------
# MAIN SCRAPER
# -------------------------------------------------
for subcat in subcats:

    subcat_id = subcat["subcat_id"]
    subcat_name = subcat["text"]
    slug = subcat_name.lower().replace(" ", "-")

    print(f"\n=== SUBCATEGORY: {subcat_name} ({subcat_id}) ===")

    product_urls = set()
    page = 1

    while True:
        api_url = API_TEMPLATE.format(slug=slug, page=page, subcat_id=subcat_id)
        print(f"[PAGE {page}] {api_url}")

        try:
            resp = requests.get(api_url, headers=HEADERS, cookies=COOKIES, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"❌ Error fetching page {page}: {e}")
            break

        # Extract HTML section
        product_html = data.get("sections", {}).get("product_list", "")

        if not product_html:
            print("⚠️ No product_list section found — stopping this category.")
            break

        # Parse HTML
        tree = html.fromstring(product_html)

        # Extract product <a href>
        links = tree.xpath("//a[@href]/@href")

        for link in links:
            product_urls.add(link)

        print(f" → Extracted {len(links)} links (total: {len(product_urls)})")

        # Pagination check
        total_pages = data.get("total_pages", 1)

        if page >= total_pages:
            print(f"✔ Finished: reached last page ({total_pages})")
            break

        page += 1
        sleep(1)   # polite delay

    # Save this subcategory's results
    output[subcat_name] = {
        "subcat_id": subcat_id,
        "total_urls": len(product_urls),
        "urls": sorted(product_urls)
    }

# -------------------------------------------------
# SAVE OUTPUT JSON
# -------------------------------------------------
with open("product_urls.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n🎉 DONE! All product URLs saved to product_urls.json")
