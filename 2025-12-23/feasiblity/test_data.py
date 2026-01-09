# import requests
# from parsel import Selector
# import json
# import time

# HEADERS = {
#     "User-Agent": "Mozilla/5.0",
# }

# BASE = "https://www.portwest.com"

# INPUT_FILE = "portwest_product_urls.txt"
# OUTPUT_FILE = "portwest_pdp_data.json"

# results = []

# # ---------------------------
# # Read product URLs
# # ---------------------------
# with open(INPUT_FILE, "r", encoding="utf-8") as f:
#     product_urls = [line.strip() for line in f if line.strip()]

# print(f"Loaded {len(product_urls)} product URLs")

# # ---------------------------
# # Parse each PDP
# # ---------------------------
# for url in product_urls:
#     print(f"Scraping PDP: {url}")

#     r = requests.get(url, headers=HEADERS, timeout=30)
#     if r.status_code != 200:
#         continue

#     sel = Selector(text=r.text)

#     # ---------------------------
#     # BASIC INFO
#     # ---------------------------
#     title = sel.xpath('//div[@class="col-lg-6"]//h2[1]/text()').get()
#     title = title.strip() if title else ""

#     sku = title.split("-")[0].strip() if "-" in title else ""

#     colour = sel.xpath('//div[@class="ratings-container"]//h2/text()').get(default="").strip()

#     size_range = sel.xpath('//label[contains(text(),"Size Range")]/following-sibling::div/text()').get(default="").strip()

#     # ---------------------------
#     # IMAGES
#     # ---------------------------
#     images = sel.xpath('//img[contains(@class,"product-single-image")]/@src').getall()
#     images = list(dict.fromkeys(images))  # dedupe

#     # ---------------------------
#     # DESCRIPTION & FEATURES
#     # ---------------------------
#     description = sel.xpath('//section[@id="content3"]//p[@class="text-justify"]/text()').get(default="").strip()

#     features = sel.xpath('//section[@id="content3"]//li/text()').getall()
#     features = [f.strip() for f in features if f.strip()]

#     fabric_title = sel.xpath('//div[contains(text(),"Shell Fabric")]/text()').get(default="").strip()
#     fabric_value = sel.xpath('//div[contains(text(),"Shell Fabric")]/following-sibling::div/text()').get(default="").strip()

#     # ---------------------------
#     # WASHCARE
#     # ---------------------------
#     washcare = sel.xpath('//h3[contains(text(),"Washcare")]/following-sibling::table//img/@title').getall()

#     # ---------------------------
#     # DOCUMENTS
#     # ---------------------------
#     documents = []
#     for a in sel.xpath('//h3[contains(text(),"Documentation")]/following-sibling::ul//a'):
#         documents.append({
#             "name": a.xpath('text()').get(),
#             "url": a.xpath('@href').get()
#         })

#     # ---------------------------
#     # COLOURS (ALL VARIANTS)
#     # ---------------------------
#     colours = sel.xpath('//ul[@class="config-swatch-list"]//a/@href').getall()
#     colours = [BASE + c for c in colours]

#     # ---------------------------
#     # BUILD RECORD
#     # ---------------------------
#     item = {
#         "pdp_url": url,
#         "brand": "Portwest",
#         "product_name": title,
#         "sku_mpn": sku,
#         "colour": colour,
#         "size_range": size_range,
#         "images": images,
#         "description": description,
#         "features": features,
#         "fabric": f"{fabric_title} {fabric_value}".strip(),
#         "washcare": washcare,
#         "documents": documents,
#         "colour_variants": colours,

#         # Not available on PDP
#         "gtin": "",
#         "uom": "",
#         "quantities": "",
#         "intrastat_code": ""
#     }

#     results.append(item)
#     time.sleep(0.6)

# # ---------------------------
# # SAVE OUTPUT
# # ---------------------------
# with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#     json.dump(results, f, indent=2, ensure_ascii=False)

# print(f"\nSaved {len(results)} PDP records to {OUTPUT_FILE}")




import requests
import json
import os
import time
from parsel import Selector
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,*/*"
}

INPUT_FILE = "portwest_product_urls.txt"
OUT_DIR = "portwest_pdp_output"
os.makedirs(OUT_DIR, exist_ok=True)


def clean(text):
    return text.strip() if text else None


def scrape_product(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    sel = Selector(text=r.text)

    # ---------------- BASIC ----------------
    product_name = clean(sel.xpath('//h2/text()').get())
    colour = clean(sel.xpath('//div[@class="ratings-container"]//h2/text()').get())

    style_code = None
    if product_name and "-" in product_name:
        style_code = product_name.split("-")[0].strip()

    # ---------------- IMAGES ----------------
    images = list(set(
        sel.xpath('//img[@class="product-single-image"]/@src').getall()
    ))

    # ---------------- COLOURS ----------------
    colours = []
    for a in sel.xpath('//ul[@class="config-swatch-list"]/li/a'):
        colours.append({
            "url": urljoin(url, a.xpath('@href').get()),
            "image": a.xpath('.//img/@src').get()
        })

    # ---------------- SIZE ----------------
    size_range = clean(
        sel.xpath('//label[contains(text(),"Size Range")]/following-sibling::div/text()').get()
    )

    # ---------------- DESCRIPTION ----------------
    description = clean(
        sel.xpath('//p[@class="text-justify"]/text()').get()
    )

    features = [
        clean(f) for f in sel.xpath('//section[@id="content3"]//li/text()').getall()
        if clean(f)
    ]

    # ---------------- FABRIC ----------------
    shell_fabric = clean(
        sel.xpath('//div[contains(text(),"Shell Fabric")]/following-sibling::div/text()').get()
    )

    # ---------------- DOCUMENTS ----------------
    documents = {}
    for a in sel.xpath('//section[@id="content4"]//a'):
        key = clean(a.xpath('text()').get())
        link = a.xpath('@href').get()
        if key and link:
            documents[key.lower().replace(" ", "_")] = link

    # ---------------- WASHCARE ----------------
    washcare = []
    for img in sel.xpath('//table//img'):
        washcare.append({
            "icon": img.xpath('@src').get(),
            "title": img.xpath('@title').get()
        })

    # ---------------- FINAL DATA ----------------
    return {
        "brand": "Portwest",
        "product_name": product_name,
        "style_code": style_code,
        "mpn": style_code,
        "gtin": None,
        "uom": None,
        "quantity": None,
        "intrastat_code": None,
        "pdp_url": url,
        "colour": colour,
        "size_range": size_range,
        "description": description,
        "features": features,
        "shell_fabric": shell_fabric,
        "images": images,
        "colour_variants": colours,
        "documents": documents,
        "washcare": washcare
    }


# ---------------- RUN (SAVE ONE BY ONE) ----------------
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    product_urls = [u.strip() for u in f if u.strip()]

for url in product_urls:
    try:
        print(f"Scraping → {url}")
        data = scrape_product(url)

        filename = f"{data['style_code']}_{data['colour']}.json"
        filename = filename.replace(" ", "_").replace("/", "_")

        with open(os.path.join(OUT_DIR, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Saved → {filename}")
        time.sleep(0.8)

    except Exception as e:
        print(f"❌ Error on {url}: {e}")
