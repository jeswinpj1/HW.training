from lxml import html
import json

def parse_product(file_path):
    """Extract product details from a saved PDP HTML"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    tree = html.fromstring(content)

    product = {
        "unique_id": "N/A",
        "product_name": "N/A",
        "brand": "N/A",
        "category": "",
        "selling_price": "N/A",
        "regular_price": "N/A",
        "promotion_description": "N/A",
        "product_description": "",
        "currency": "N/A",
        "color": "N/A",
        "size": "N/A",
        "rating": "N/A",
        "reviews": "N/A",
        "material_composition": "N/A",
        "style": "N/A",
        "care_instructions": "N/A",
        "features": [],
        "images": []
    }

    # --- Extract JSON-LD data ---
    scripts = tree.xpath('//script[@type="application/ld+json"]/text()')
    for script in scripts:
        try:
            data = json.loads(script)
            if isinstance(data, dict) and data.get("@type") == "Product":
                product["unique_id"] = data.get("sku", "N/A")
                product["product_name"] = data.get("name", "N/A")
                if "brand" in data:
                    product["brand"] = data["brand"]["name"] if isinstance(data["brand"], dict) else data["brand"]
                if "offers" in data:
                    product["selling_price"] = data["offers"].get("price", "N/A")
                    product["currency"] = data["offers"].get("priceCurrency", "N/A")
                if "description" in data:
                    product["product_description"] = data["description"]
        except:
            continue

    # --- Breadcrumbs for category ---
    categories = tree.xpath('//nav[@data-testid="breadcrumbs"]//a/text()')
    product["category"] = " > ".join([c.strip() for c in categories if c.strip()])

    # --- Price (extra check from DOM) ---
    prices = tree.xpath('//span[contains(@class,"price")]/text()')
    if prices:
        product["selling_price"] = prices[0].strip()
        product["regular_price"] = prices[-1].strip()

    # --- Promotion ---
    promo = tree.xpath('//span[contains(@class,"promo")]/text()')
    if promo:
        product["promotion_description"] = promo[0].strip()

    # --- Features ---
    features = tree.xpath('//ul[contains(@class,"features")]//li/text()')
    product["features"] = [f.strip() for f in features if f.strip()]

    # --- Material / Style / Care ---
    material = tree.xpath('//li[contains(text(),"Composition")]/text()')
    if material:
        product["material_composition"] = material[0].strip()

    style = tree.xpath('//li[contains(text(),"Style")]/text()')
    if style:
        product["style"] = style[0].strip()

    care = tree.xpath('//li[contains(text(),"Care")]/text()')
    if care:
        product["care_instructions"] = care[0].strip()

    # --- Rating ---
    rating = tree.xpath('//span[contains(@class,"average-rating")]/text()')
    if rating:
        product["rating"] = rating[0].strip()

    reviews = tree.xpath('//span[contains(@class,"review-count")]/text()')
    if reviews:
        product["reviews"] = reviews[0].strip()

    # --- Images ---
    images = tree.xpath('//img[contains(@class,"media")]/@src | //img[contains(@class,"media")]/@data-src | //img/@srcset')
    product["images"] = list(set(images))

    return product
if __name__ == "__main__":
    file_path = "plp.html"   # your saved product detail HTML
    data = parse_product(file_path)

    # Print in terminal
    print("\n=== Product Details ===")
    for key, value in data.items():
        print(f"{key}: {value}")

    # Save into JSON file
    with open("product.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("\n Product details saved to product.json")
