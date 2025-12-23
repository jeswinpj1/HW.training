import requests
from parsel import Selector

response = requests.get(
    'https://www.portwest.com',
)

print(response.status_code)

sel = Selector(text=response.text)

hrefs = sel.xpath('//div[@class="menu-title"]/a/@href').getall()

#...................................
# carwler
#...................................

for cat_url in category_urls:

    # Example path:
    # /products/footwear/X/2/5
    parts = urlparse(cat_url).path.strip("/").split("/")

    if len(parts) < 5:
        continue

    level = parts[2]        # X
    group = parts[3]        # 2
    category_id = parts[4]  # 5

    offset = 24

    while True:
        api_url = (
            f"{BASE}/products/load_more_category_products/"
            f"{level}/{group}/{category_id}/{offset}"
        )

        print(f"Fetching: {api_url}")
        r = requests.get(api_url, headers=HEADERS, timeout=30)

        if r.status_code != 200 or not r.text.strip():
            break

        sel = Selector(text=r.text)

        product_links = sel.xpath(
            '//div[contains(@class,"product")]'
            '//a[contains(@href,"/products/view")]/@href'
        ).getall()

        if not product_links:
            break

        for link in product_links:
            all_products.add(BASE + link)

        print(f"  → {len(product_links)} products")

        offset += 24
        time.sleep(0.8)

#...................................
# parser
#...................................


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


#...................................
# findings
#...................................

# 1. count is basically count on rough figure
# 2. some images are not available (in site shown (coming soon))