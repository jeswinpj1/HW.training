import requests
import random
from scrapy import Selector
import time

# ---------------------------------- HEADERS ---------------------------------- #
headers = {
    "accept": "application/json, text/html, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-GB,en;q=0.9",
    "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Linux\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}

# ---------------------------------- CRAWLER SECTION ---------------------------------- #
base_url = "https://wasalt.sa/en/sale/search?countryId=1&propertyFor=sale&type=residential"
last_page = 20  

total_links = 0
all_property_links = []

print("\n------------------ START: WASALT FEASIBILITY CHECK ------------------\n")

for page in range(1, last_page + 1):
    url = f"{base_url}&page={page}"
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        print(f"[PAGE {page}] Status:", response.status_code)

        if response.status_code == 200:
            sel = Selector(text=response.text)
            links = sel.xpath("//div[contains(@class,'styles_cardContent__')]/a/@href").extract()
            full_links = ["https://wasalt.sa" + i if i.startswith("/") else i for i in links]

            print(f" → Found {len(full_links)} property links")
            total_links += len(full_links)
            all_property_links.extend(full_links)
        else:
            print(f" → Failed to load page {page}")

        time.sleep(1)  # polite delay

    except Exception as e:
        print(f"[PAGE {page}] Error:", e)

print("\n------------------ SUMMARY ------------------")
print(f"Total pages checked : {last_page}")
print(f"Total property URLs : {total_links}")
print("--------------------------------------------------\n")

# ---------------------------------- PARSER (TEST SINGLE PROPERTY) ---------------------------------- #
if all_property_links:
    test_url = all_property_links[0]
else:
    test_url = "https://wasalt.sa/en/property/12345"  # placeholder

try:
    res = requests.get(test_url, headers=headers, proxies=proxies, timeout=30)
    print(f"Testing Property Page: {test_url}")
    print("Status:", res.status_code)

    if res.status_code == 200:
        sel = Selector(text=res.text)

        title = sel.xpath("//h1/text()").extract_first()
        price = sel.xpath("//div[contains(@class,'style_price__')]/text()").extract_first()
        location = sel.xpath("//div[contains(@class,'stylenewPDP_propInfoAdd__')]/text()").extract()

        print("Title     :", title)
        print("Price     :", price)
        print("Location  :", " ".join([i.strip() for i in location if i.strip()]))

except Exception as e:
    print("Error fetching property page:", e)

# ---------------------------------- FINDINGS ---------------------------------- #
#  Pagination available
#  Property cards located in div.styles_cardContent__
#  Detail page contains title, price, location & specification data
#  No login/token required
#  Property detail URL ID changes dynamically
#  Suitable for full crawler + parser development

