import requests
from parsel import Selector
from urllib.parse import urljoin

BASE = "https://www.fivebelow.com"

response = requests.get(BASE)
sel = Selector(text=response.text)

all_urls = sel.xpath(
    '//div[contains(@class,"relative") and contains(@class,"w-full")]//a/@href'
).getall()

filtered = []

for u in all_urls:
    full = urljoin(BASE, u)
    if "candy" in full.lower() or "toys-and-games" in full.lower():
        filtered.append(full)

# ✅ remove duplicates
unique_urls = list(dict.fromkeys(filtered))

for u in unique_urls:
    print(u)

print("TOTAL UNIQUE:", len(unique_urls))

