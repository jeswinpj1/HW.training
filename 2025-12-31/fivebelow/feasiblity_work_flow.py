import requests
from parsel import Selector
from urllib.parse import urljoin

BASE = "https://www.fivebelow.com"
#...........................................
# CRAWLER 
#...........................................
CATEGORY_URLS = [
    "https://www.fivebelow.com/categories/candy",
    "https://www.fivebelow.com/categories/toys-and-games",
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

all_subcats = []

for cat_url in CATEGORY_URLS:
    print(f"Scraping: {cat_url}")

    resp = requests.get(cat_url, headers=headers, timeout=30)
    sel = Selector(text=resp.text)

    sub_urls = sel.xpath(
        '//a[contains(@class,"inline-block") '
        'and contains(@class,"cursor-pointer")]/@href'
    ).getall()

    for u in sub_urls:
        full = urljoin(BASE, u)
        all_subcats.append(full)

#  remove duplicates + preserve order
unique_subcats = list(dict.fromkeys(all_subcats))

def get_last_page(sel):
    """
    Extract last page number from pagination
    """
    last_page_url = sel.xpath(
        '//a[contains(@title,"last page")]/@href'
    ).get()

    if not last_page_url:
        return 1

    qs = parse_qs(urlparse(last_page_url).query)
    return int(qs.get("p", [1])[0])

all_products = []

for sub_url in subcategories:

    # page 1
    resp = requests.get(sub_url, headers=HEADERS, timeout=30)
    sel = Selector(text=resp.text)

    last_page = get_last_page(sel)
    

    for page in range(1, last_page + 1):
        page_url = f"{sub_url}?p={page}"
        

        r = requests.get(page_url, headers=HEADERS, timeout=30)
        s = Selector(text=r.text)

        product_urls = s.xpath(
            '//a[contains(@class,"absolute") and contains(@class,"size-full")]/@href'
        ).getall()

        for u in product_urls:
            all_products.append(urljoin(BASE, u))


#  remove duplicates, preserve order
unique_products = list(dict.fromkeys(all_products))

#...............................................................
# PARSER
#...............................................................


def parse_product(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    sel = Selector(text=r.text)

    data = {
        "id": sel.xpath('//input[@name="productId"]/@value').get(default="") or url.split("-")[-1],
        "url": url,
        "title": sel.xpath('//div[@class="relative flex pr-40"]/h1/text()').get(default="").strip(),
        "price": sel.xpath('(//p[contains(@class,"text-fivebelow-blue")])[1]/text()').get(default="").strip().replace("$",""),
        "images": list(dict.fromkeys(sel.xpath('//div[contains(@class,"relative")]/div/img/@src').getall())),
        "sku": sel.xpath('string(//span[contains(@class,"my-10")])').get(default="").replace("item #","").strip(),
        "description_items": [item.strip() for item in sel.xpath('//div[contains(@id,"headlessui-disclosure-panel")]//ul/li/text()').getall() if item.strip()]
    }
    return data

