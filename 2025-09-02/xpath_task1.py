import requests
from lxml import html
import re

url = "https://www2.hm.com/en_in/productpage.1306054001.html"
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "origin": "https://www2.hm.com",
    "referer": "https://www2.hm.com/",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
}

response = requests.get(url, headers=headers)
print(response.status_code)
tree = html.fromstring(response.content)
title = tree.xpath('//h1/text()')
title_clean = title[0].strip() if title else "N/A"

price = tree.xpath('//span[@class="a15559 b6e218 bf4f3a"]/text()')
if price:
    price_str = price[0].strip()[4:] if price else "N/A"
    price_clean = re.sub(r'[^\d.]', '', price_str)
else:
    price_clean = "N/A"

colour = tree.xpath('//section[@data-testid="color-selector"]//p/text()')
colour_clean = colour[0].strip() if colour else "N/A"

print(f"Title: {title_clean}")
print(f"Price: {price_clean}")
print(f"Colour: {colour_clean}")
