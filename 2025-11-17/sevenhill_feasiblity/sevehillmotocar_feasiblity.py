
import requests
from parsel import Selector
from urllib.parse import urljoin
import json

BASE_URL = "https://www.sevenhillsmotorcars.com"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
}

# ------------------------------
# CRAWLER TEST — COLLECT PRODUCT URLS
# ------------------------------
def test_crawler():
    url = f"{BASE_URL}/vehicles"
    response = requests.get(url, headers=headers)
    sel = Selector(response.text)

    product_urls = sel.xpath(
        '//div[contains(@class,"sh-vehicle-row")]//a[@class="sh-inventory-item"]/@href'
    ).getall()

    product_urls = [urljoin(BASE_URL, u) for u in product_urls]

    return product_urls


# ------------------------------
# PARSER TEST — SINGLE PRODUCT
# ------------------------------
def test_parser(product_url="https://www.sevenhillsmotorcars.com/vehicles/1969-chevrolet-camaro-z28/12792"):
    resp = requests.get(product_url, headers=headers)
    sel = Selector(resp.text)

    PRODUCT_TITLE = "normalize-space(//h1/text() | //title/text())"

    page_title = sel.xpath(PRODUCT_TITLE).get() or ""
    page_title = page_title.split("|")[0].strip()

    # Extract year/make/model
    year, make, model = "N/A", "N/A", "N/A"
    title_parts = page_title.split(" ", 2)
    if len(title_parts) >= 1 and title_parts[0].isdigit():
        year = title_parts[0]
        if len(title_parts) >= 2: make = title_parts[1]
        if len(title_parts) >= 3: model = title_parts[2]

    # Extract vehicle attributes
    item = {
        "source_link": product_url,
        "full_title": page_title,
        "year": year,
        "make": make,
        "model": model,
        "vin": sel.xpath('normalize-space(//dt[contains(., "Vin")]/following-sibling::dd/text())').get(),
        "stock_no": sel.xpath('normalize-space(//dt[contains(., "Stock")]/following-sibling::dd/text())').get(),
        "price": sel.xpath('normalize-space(//dt[contains(., "Price")]/following-sibling::dd/text())').get(),
        "mileage": sel.xpath('normalize-space(//dt[contains(., "Miles")]/following-sibling::dd/text())').get(),
        "transmission": sel.xpath('normalize-space(//dt[contains(., "Transmission")]/following-sibling::dd/text())').get(),
        "engine": sel.xpath('normalize-space(//dt[contains(., "Engine")]/following-sibling::dd/text())').get(),
        "exterior_color": sel.xpath('normalize-space(//dt[contains(., "Exterior")]/following-sibling::dd/text())').get(),
        "interior_color": sel.xpath('normalize-space(//dt[contains(., "Interior")]/following-sibling::dd/text())').get(),
        "body_style": sel.xpath('normalize-space(//dt[contains(., "Body Style")]/following-sibling::dd/text())').get(),
        "description": sel.xpath('normalize-space(//div[contains(@id, "description") or contains(@class, "vehicle-description")])').get(),
        "image_urls": sel.xpath('//div[contains(@class, "vehicle-photos")]//img/@src | //a[contains(@class, "gallery")]/@href').getall(),
    }

    return item

# ------------------------------
# FEASIBILITY FINDINGS
# ------------------------------
# findings :
#     "pagination": "Works — next_page is inside <li class='next_page'> but must check disabled state.",
#     "url_pattern": "URLs do NOT change by color/variant. One page per vehicle.",
#     "structure": "Vehicle details always provided in <dt>/<dd> tag pairs.",
#         "Site uses static HTML; low risk of blocking.",
#         "No dynamic JS rendering needed.",
#         "Pagination classes sometimes include extra spaces; handle with contains()."
   