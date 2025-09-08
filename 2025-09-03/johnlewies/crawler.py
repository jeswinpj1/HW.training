from lxml import html
import json

def get_top_categories(tree):
    """Extract top categories"""
    categories = []
    top_nodes = tree.xpath('//nav[contains(@class,"DesktopMenu")]//li')
    for node in top_nodes:
        link = node.xpath('.//a/@href')
        name = node.xpath('.//a/text()')
        if link and "/c" in link[0]:
            categories.append({
                "name": name[0].strip() if name else "N/A",
                "url": link[0],
                "subcategories": []
            })
    return categories

def get_sub_categories(node):
    """Extract subcategories from a category node"""
    subcategories = []
    sub_links = node.xpath('.//a[contains(@href,"/browse/")]')
    for a in sub_links:
        href = a.xpath('./@href')
        name = "".join(a.xpath('.//text()')).strip()
        if href:
            subcategories.append({
                "name": name,
                "url": href[0],
                "products": []
            })
    return subcategories

def get_products(tree):
    """Extract product (PDP) URLs"""
    product_links = tree.xpath('//article[contains(@class,"product-card")]//a/@href')
    return list(set(product_links))

if __name__ == "__main__":
    file_path = "plp.html"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    tree = html.fromstring(content)

    categories = get_top_categories(tree)

    for cat in categories:
        sub_nodes = tree.xpath(f'//a[contains(@href,"{cat["url"].split("/")[-1]}")]//..')
        for node in sub_nodes:
            subs = get_sub_categories(node)
            cat["subcategories"].extend(subs)
    products = get_products(tree)
    for cat in categories:
        for sub in cat["subcategories"]:
            sub["products"] = products[:5] 
 
    print("\n=== Category Hierarchy ===")
    for cat in categories:
        print(f"Top: {cat['name']} → {cat['url']}")
        for sub in cat["subcategories"]:
            print(f"   Sub: {sub['name']} → {sub['url']}")
            for p in sub["products"]:
                print(f"      Product: {p}")
    with open("categories_hierarchy.json", "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=4, ensure_ascii=False)

    print("\n Saved hierarchy to categories_hierarchy.json")
