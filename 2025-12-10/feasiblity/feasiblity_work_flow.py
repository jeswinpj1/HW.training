# from curl_cffi import requests
import requests
from scrapy import Selector
import json
from pymongo import MongoClient

# -------------------------
# CONFIG
# -------------------------


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# -------------------------
# INPUT BASE CRAWLER
# -------------------------
CATEGORY_URL = "https://www.pharmamarket.be/be_fr/insider/search/query/?q=magnesium"
response = requests.get(CATEGORY_URL, headers=headers)
selector = Selector(text=response.text)

# Collect product URLs
product_urls = selector.xpath('//a[@class="cs-product-tile__name-link product-item-link"]/@href').getall()
product_urls = ["https://www.pharmamarket.be" + url for url in product_urls]

# -------------------------
# PARSER / EXTRACTOR
# -------------------------
def extract_details(html):
    sel = Selector(text=html)

    title = sel.xpath('//h1[contains(@class,"page-title")]//span/text()').get()
    if title:
        title = title.strip()

    # Price
    price_raw = sel.xpath('//span[contains(@id,"product-price")]/@data-price-amount').get()
    price_display = sel.xpath('//span[contains(@id,"product-price")]/span[@class="price"]/text()').get()
    old_price = sel.xpath('//p[@class="old-price"]//span[@class="price"]/text()').get()
    if old_price and price_display:
        price_display = f"{price_display} (Old Price: {old_price})"

    # Stock
    stock = sel.xpath('//div[@class="pharmamarket-deliveryinformation"]/b/text()').get()

    # Discount
    discount = "".join(sel.xpath('//span[@class="cs-page-product__badge-text"]//text()').getall()).strip()

    # Breadcrumbs
    breadcrumbs = sel.xpath('//ul[@class="cs-breadcrumbs__list"]//li//span//text()').getall()

    # Description
    desc = " ".join(sel.xpath('//div[@class="product attribute description"]//text()').getall()).strip()

    # Images
    images = sel.xpath('//div[@class="cs-page-product__gallery"]//picture//source/@srcset').getall()
    if not images:
        images = sel.xpath('//div[@class="cs-page-product__gallery"]//picture//img/@src').getall()
    images = list(set(images))
    image_main = sel.xpath('//div[contains(@class,"fotorama__stage__frame")]//img/@src').get()

    # Attributes
    attributes = {}
    rows = sel.xpath('//table[@id="product-attribute-specs-table"]//tr')
    for r in rows:
        key = r.xpath('./th/text()').get()
        value = r.xpath('./td/text()').get()
        if key and value:
            attributes[key.strip()] = value.strip()

    # Brand
    brand = sel.xpath('//ul[@class="product-brand"]//img/@alt').get()

# -------------------------
# RUN PARSER
# -------------------------
for url in product_urls:
    response = requests.get(url, headers=headers)
    result = extract_details(response.text)
    print(json.dumps(result, ensure_ascii=False, indent=2))

# -------------------------
# findings
# -------------------------
# 1. A single input can return multiple results.

# 2. Searching by EAN Master and CNK Belux inputs returns none.

# 3. Searching by the PRODUCT GENERAL NAME lists products from the same brand, though finding similar products can be difficult.

# 4. Almost all input records partially match the product name, but do not match either the EAN Master or the CNK Belux
