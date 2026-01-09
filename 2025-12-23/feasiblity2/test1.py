import requests
from parsel import Selector
from urllib.parse import urljoin

url = "https://eu.targus.com"
output_file = "targus_grandchild_urls.txt"

response = requests.get(url, timeout=30)
print("Status:", response.status_code)

sel = Selector(response.text)

# extract hrefs
urls = sel.xpath('//a[@class="grandchildlink"]/@href').getall()
print("Found:", len(urls))

# make absolute URLs + dedupe
final_urls = []
for u in urls:
    full_url = urljoin(url, u)
    if full_url not in final_urls:
        final_urls.append(full_url)

# save to txt (one per line)
with open(output_file, "w", encoding="utf-8") as f:
    for u in final_urls:
        f.write(u + "\n")

print(f"Saved {len(final_urls)} URLs to {output_file}")
