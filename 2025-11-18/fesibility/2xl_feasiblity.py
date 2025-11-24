
import requests
from lxml import html
import json
from time import sleep

BASE_URL = "https://2xlhome.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

API_TEMPLATE = (
    "https://2xlhome.com/ae-en/{slug}?p={page}&p={page}"
    "&_category_id={subcat_id}"
    "&_core_filters=W10%3D"
    "&_sections=product_list"
    "&isPowerListingAjax=b6bdd9ecd08caf7084a957e7d3e2126b"
)

COOKIES = {
    "PHPSESSID": "7fc1779817d0b383b7cc5606712246d2",
    "form_key": "d34LJvkYZTYtL88X",
    "_ga": "GA1.1.1807385951.1758085159"
}

# -----------------------------------------
# 1. SUBCATEGORY EXTRACTION
# -----------------------------------------
def extract_subcategories():
    print("🔍 Extracting menu subcategories…")
    resp = requests.get(BASE_URL, headers=HEADERS)
    resp.raise_for_status()

    tree = html.fromstring(resp.content)
    li_elements = tree.xpath("//li[@data-subcat-id]")

    subcats = []
    for li in li_elements:
        subcat_id = li.get("data-subcat-id")
        a = li.find(".//a")
        subcat_name = a.text_content().strip() if a is not None else None

        subcats.append({
            "subcat_id": subcat_id,
            "text": subcat_name
        })

    print(f"✔ Found {len(subcats)} subcategories")
    return subcats


# -----------------------------------------
# 2. PRODUCT LISTING CRAWLER
# -----------------------------------------
def crawl_subcategory(subcat):
    subcat_id = subcat["subcat_id"]
    subcat_name = subcat["text"]
    slug = subcat_name.lower().replace(" ", "-")

    product_urls = set()
    page = 1

    while True:
        api_url = API_TEMPLATE.format(slug=slug, page=page, subcat_id=subcat_id)
        try:
            resp = requests.get(api_url, headers=HEADERS, cookies=COOKIES, timeout=30)
            data = resp.json()
        except Exception as e:
            break

        product_html = data.get("sections", {}).get("product_list", "")
        if not product_html:
            break

        tree = html.fromstring(product_html)
        links = tree.xpath("//a[@href]/@href")

        for link in links:
            product_urls.add(link)

        total_pages = data.get("total_pages", 1)
        if page >= total_pages:
            break
        page += 1
        sleep(1)

    return sorted(product_urls)


# -----------------------------------------
# 3. PRODUCT PARSER
# -----------------------------------------
def parse_product(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print("❌ Failed:", url)
            return None

        tree = html.fromstring(resp.text)

        # BASIC INFO
        product_id = extract_first(tree, "//div[contains(@class,'price-box')]/@data-product-id")
        product_name = extract_first(tree, "//h1[@class='page-title']//span[@itemprop='name']/text()")
        product_type = extract_first(tree, "//div[@itemprop='sku']/text()")

        # PRICES
        price = extract_first(tree, "//span[@id][contains(@id,'product-price')]/text()")
        was_price = extract_first(tree, "//span[@id][contains(@id,'old-price')]/text()")
        discount = extract_first(tree, "//span[contains(@class,'discountper')]/text()")

        # STOCK
        stock = extract_first(tree, "//div[contains(@class,'stock')]/span/text()")
        quantity = extract_first(tree, "//input[@name='qty']/@value")

        # IMAGES
        images = tree.xpath("//img[contains(@class,'fotorama__img')]/@src")
        images = [clean(i) for i in images if clean(i)]

        # SPECIFICATIONS
        specification = {}
        spec_rows = tree.xpath("//div[@class='value']")
        for row in spec_rows:
            key_el = row.xpath(".//strong/text()")
            key = clean(key_el[0]) if key_el else ""
            val = clean(" ".join(row.xpath(".//text()"))) if key else ""
            if key:
                val = val.replace(key, "").strip()
                specification[key] = val

        product_color = specification.get("Color:", "")
        material = specification.get("Material:", "")

        # DESCRIPTION
        details_text = tree.xpath("//div[@id='description']//text()")
        details_string = " ".join([clean(t) for t in details_text if clean(t)])


# -----------------------------------------
# 5. FINDINGS (To be used manually)
# -----------------------------------------
"""
FINDINGS
========
 Subcategories available via <li data-subcat-id>.
 API requires slug + subcat_id combination.
 product_list HTML returned from API → parseable.
 Pagination handled via "total_pages".
 Product detail page contains clean HTML structure.
 Some products may return missing fields.
"""
