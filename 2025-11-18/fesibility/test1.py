import requests
from lxml import html
import json

url = "https://2xlhome.com"  # or any page that contains menu
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

resp = requests.get(url, headers=headers)
resp.raise_for_status()

tree = html.fromstring(resp.content)

# XPath to find <li> having data-subcat-id
# This assumes something like: <li ... data-subcat-id="..."><a>Text</a></li>
li_elements = tree.xpath("//li[@data-subcat-id]")

data = []
for li in li_elements:
    subcat_id = li.get("data-subcat-id")
    # find the <a> child
    a = li.find(".//a")
    text = a.text_content().strip() if a is not None else None
    data.append({
        "subcat_id": subcat_id,
        "text": text
    })

# Save to JSON
with open("subcats.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Extracted:",len(data))
