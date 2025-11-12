import requests
from parsel import Selector
import json
import time
############################## HEADERS & SETUP ##############################

BASE_URL = "https://classiccars.com/listings/find/until-1990"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.classiccars.com/",
    "Connection": "keep-alive",
}

cookies = {
    "IDE": "AHWqTUkOeRTNh07YhdhUD176dl3is_181CUVbLfHUzDhrBJt7Oj6pRD_hha5KKGkPu4",
    "DSID": "AEhM4MfwkxlssRFoHWRFN-HIBBA0Wkv21MqEMJpvO5mjya5kQgqh-mwVXswfNp_mDP-PPAxaeXf2Cz6VCB9lYuu63G8n82egqk3KiKNHSUF3P50Ru_PyoJfjlqKvOrKy8MHrxOHxkDrxnMRMtGTTdgc0NwGGigl0mceTqcbl47u8FfIsyI1zCjQ9Tt_sB6JVilPfJ1xyXgJygkl7eNamD8IaJthw2YZj4l_T-0NMLJdWedMDsqcCkvrXzJY4K7rQn9Y5N1MKRjjJJkeRDCoh6m7uKLGAa4FyzzTANStQDnJ7i_1y8TbR4TY",
}


############################## CRAWLER TEST ##############################
page = 1
test_urls = []
while page <= 2:  # check first two pages for structure
    url = f"{BASE_URL}?p={page}"
    print(f"Fetching page {page} → {url}")
    response = requests.get(url, headers=headers, cookies=cookies, timeout=30)

    if response.status_code != 200:
        print(f" Failed to fetch page {page}: {response.status_code}")
        break
    sel = Selector(text=response.text)
    links = sel.xpath('//a[@class="d-block w100 dark-link"]/@href').getall()
    if not links:
        break
    for link in links:
        full_url = (
            link if link.startswith("https") else f"https://classiccars.com{link}"
        )
        test_urls.append(full_url)

    next_page = sel.xpath(
        '//li[@class="active "]/following-sibling::li[1]/a/@href'
    ).get()
    if not next_page:
        print(" No more pages found.")
        break

    page += 1
    time.sleep(0.5)
############################## PARSER TEST ##############################
if test_urls:
    test_url = test_urls[0]
    print(f"Parsing test listing → {test_url}")
    response = requests.get(test_url, headers=headers, cookies=cookies, timeout=30)
    sel = Selector(text=response.text)

    car_data = {
        "title": sel.xpath('//h1/text()').get(default="").strip(),
        "make": sel.xpath(
            '//li[contains(@class,"p-manufacturer")]//span[contains(@class,"gray")]/text()'
        ).get(default="").strip(),
        "model": sel.xpath(
            '//li[contains(@class,"p-model")]//span[contains(@class,"gray")]/text()'
        ).get(default="").strip(),
        "year": sel.xpath(
            '//li[contains(@class,"dt-start")]//span[contains(@class,"gray")]/text()'
        ).get(default="").strip(),
        "price": sel.xpath(
            '//li[contains(@class,"p-price")]//span[contains(@class,"red")]/text()'
        ).get(default="").strip(),
        "mileage": sel.xpath(
            '//li[contains(@class,"p-odometer")]//span[contains(@class,"gray")]/text()'
        ).get(default="").strip(),
        "engine": sel.xpath(
            '//li[contains(@class,"p-engine")]//span[contains(@class,"gray")]/text()'
        ).get(default="").strip(),
        "transmission": sel.xpath(
            '//li[contains(@class,"p-transmission")]//span[contains(@class,"gray")]/text()'
        ).get(default="").strip(),
        "description": " ".join(
            d.strip()
            for d in sel.xpath('//div[contains(@class,"description")]//text()').getall()
            if d.strip()
        ),
        "images": [
            img if img.startswith("http") else f"https://classiccars.com{img}"
            for img in sel.xpath(
                '//div[@id="MCThumbsRapper"]//img/@src | //div[@id="MCThumbsRapper"]//img/@data-src'
            ).getall()
        ],
    }

############################## FINDINGS ##############################
"""
Pagination works via parameter `?p=`, easy to iterate.
Product URLs follow consistent pattern .# identify valid listings and prevents confusion with non-product links (ads, banners, etc.).
Data accessible directly in HTML; no JS rendering required.
All major specs (make, model, year, price, engine, etc.) visible in <li> tags.
No color/varian data found.
Image URLs load correctly.
Requires cookie persistence for stable crawling (avoid blocking).
"""