import requests
from parsel import Selector

response = requests.get(
    'https://www.portwest.com',
)

print(response.status_code)

sel = Selector(text=response.text)

hrefs = sel.xpath('//div[@class="menu-title"]/a/@href').getall()
print(hrefs)


print(f"Saved {len(hrefs)} links to portwest_menu_links.txt")
