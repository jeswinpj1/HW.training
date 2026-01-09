
import requests
from parsel import Selector

url = "https://www.autozone.com/p/duralast-platinum-battery-h6-efb/1070711"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/141.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Referer": "https://www.autozone.com/",
}

response = requests.get(url, headers=headers, timeout=30)
print(response.status_code)

sel = Selector(response.text)

# -------- PRODUCT DESCRIPTION --------
desc_nodes = sel.xpath(
    "//h2[@data-testid='product-description-heading']/ancestor::div[2]//text()"
).getall()

description = " ".join(
    t.strip() for t in desc_nodes if t.strip()
)

# -------- PRODUCT SPECIFICATIONS --------
specs = {}

rows = sel.xpath(
    "//h2[contains(.,'PRODUCT SPECIFICATIONS')]/ancestor::table//tbody/tr"
)

print("TOTAL ROWS FOUND:", len(rows))

for row in rows:
    key = row.xpath("normalize-space(.//th//text())").get()
    value = " ".join(
        row.xpath(".//td//text()").getall()
    ).strip()

    if key and value:
        specs[key] = value

print("\nDESCRIPTION:\n", description)
print("\nSPECIFICATIONS:")
for k, v in specs.items():
    print(f"{k}: {v}")



