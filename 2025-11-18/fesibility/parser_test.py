

import json
import requests
from lxml import html
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0 Safari/537.36"
}

def clean(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def extract_first(tree, xpath):
    res = tree.xpath(xpath)
    if not res:
        return ""
    return clean(res[0])

def parse_product(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print("Failed:", url)
            return None

        tree = html.fromstring(resp.text)

        # Basic info
        product_id = extract_first(tree, "//div[contains(@class,'price-box')]/@data-product-id")
        product_name = extract_first(tree, "//h1[@class='page-title']//span[@itemprop='name']/text()")
        product_type = extract_first(tree, "//div[@itemprop='sku']/text()")

        # Price & Discount
        price = extract_first(tree, "//span[@id][contains(@id,'product-price')]/text()")
        was_price = extract_first(tree, "//span[@id][contains(@id,'old-price')]/text()")
        discount = extract_first(tree, "//span[contains(@class,'discountper')]/text()")

        # Stock & Quantity
        stock = extract_first(tree, "//div[contains(@class,'stock')]/span/text()")
        quantity = extract_first(tree, "//input[@name='qty']/@value")

        # Images
        images = tree.xpath("//img[contains(@class,'fotorama__img')]/@src")
        thumb_images = tree.xpath("//div[contains(@class,'product media')]/img/@src")
        images = list({clean(i) for i in images + thumb_images if clean(i)})

        # Specifications
        specification = {}
        spec_rows = tree.xpath("//div[@class='value']")
        for row in spec_rows:
            key_el = row.xpath(".//strong/text()")
            key = clean(key_el[0]) if key_el else ""
            val = clean(" ".join(row.xpath(".//text()"))) if key else ""
            if key:
                val = val.replace(key, "").strip()
                specification[key] = val

        # Product color & material from specification
        product_color = specification.get("Color:", "")
        material = specification.get("Material:", "")

        # Product description
        details_text = tree.xpath("//div[@id='description']//text()")
        details_string = " ".join([clean(t) for t in details_text if clean(t)])
        for k in ["Color:", "Material:", "Height (cm):", "Width (cm):", "Length (cm):"]:
            if k in specification:
                details_string = details_string.replace(specification[k], "")

        return {
            "product_id": product_id,
            "url": url,
            "product_name": product_name,
            "product_color": product_color,
            "material": material,
            "quantity": quantity,
            "details_string": details_string.strip(),
            "specification": specification,
            "product_type": product_type,
            "price": price,
            "wasPrice": was_price,
            "discount": discount,
            "stock": stock,
            "image": images
        }

    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return None


def main():
    with open("/home/user/HW.training/product_urls.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    all_products = []
    total_requests = 0
    success = 0
    failure = 0

    for subcat, info in data.items():
        urls = info.get("urls", [])  # limit 10 per subcategory
        subcat_id = info.get("subcat_id")
        for url in urls:
            # Skip invalid URLs or category pages
            if not url.startswith("http") or "accessory" in url or "furniture" in url:
                print("Skipping category URL:", url)
                continue

            total_requests += 1
            print("Parsing product URL:", url)
            details = parse_product(url)
            if details:
                details["subcat"] = subcat
                details["subcat_id"] = subcat_id
                all_products.append(details)
                success += 1
            else:
                failure += 1

    with open("product_details.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    # Summary
    success_rate = (success / total_requests) * 100 if total_requests else 0
    failure_rate = (failure / total_requests) * 100 if total_requests else 0

    print("\n-------- SUMMARY --------")
    print(f"Total Requests: {total_requests}")
    print(f"Success: {success}")
    print(f"Failure: {failure}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Failure Rate: {failure_rate:.2f}%")
    print("--------------------------")


if __name__ == "__main__":
    main()
