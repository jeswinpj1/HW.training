from parsel import Selector
import requests
import json

url = "https://www.homedepot.ca/en/home/all-departments.html"
headers = {"User-Agent": "Mozilla/5.0"}

html = requests.get(url, headers=headers, timeout=20).text
sel = Selector(text=html)

results = []

for dept in sel.xpath('//section[@class="hdca-cms-sitemap"]/ul/li'):
    # LEVEL 1 – Department
    dept_name = dept.xpath('normalize-space(.//h2//a/text())').get()
    dept_url  = dept.xpath('.//h2//a/@href').get()

    for cat in dept.xpath('./ol/li[contains(@class,"hdca-cms-sitemap__linklist-item")]'):
        # LEVEL 2 – Category
        cat_name = cat.xpath(
            'normalize-space(.//a[contains(@class,"hdca-button2")])'
        ).get()
        cat_url = cat.xpath('.//a[contains(@class,"hdca-button2")]/@href').get()

        subcats = cat.xpath('./ol/li/a')

        # LEVEL 3 – Subcategories (if any)
        if subcats:
            for sub in subcats:
                results.append({
                    "department": dept_name,
                    "department_url": dept_url,
                    "category": cat_name,
                    "category_url": cat_url,
                    "subcategory": sub.xpath('normalize-space(text())').get(),
                    "subcategory_url": sub.xpath('@href').get()
                })
        else:
            results.append({
                "department": dept_name,
                "department_url": dept_url,
                "category": cat_name,
                "category_url": cat_url,
                "subcategory": None,
                "subcategory_url": None
            })

# -------------------------
# SAVE TO JSON FILE
# -------------------------
output_file = "homedepot_ca_full_category_tree.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Saved {len(results)} records to {output_file}")
