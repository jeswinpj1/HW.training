import json
from curl_cffi import requests
from lxml import html

# Load crawled product URLs
with open("cvs_output.json", "r", encoding="utf-8") as f:
    crawled_data = json.load(f)

BASE_URL = "https://www.cvs.com/shop"

# Proxy settings
PROXIES = {
    "http": "http://scraperapi.country_code=us:504eeef7c076dfcf401adae86875886d@proxy-server.scraperapi.com:8001",
    "https": "http://scraperapi.country_code=us:504eeef7c076dfcf401adae86875886d@proxy-server.scraperapi.com:8001"
}

# Chrome impersonation
session = requests.Session(impersonate="chrome120")
session.headers.update({
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})

def get_page(url):
    try:
        resp = session.get(url, proxies=PROXIES, timeout=30, verify=False)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return None

def parse_product(url):
    """Extract product details: title, price, brand, description"""
    page = get_page(url)
    if not page:
        return None
    
    tree = html.fromstring(page)

    try:
        title = tree.xpath('//h1[@class="text-[18px] font-medium leading-[23.4px] tracking-[0px]"]/text()')[0].strip()
    except:
        title = None

    try:
        price = tree.xpath('//span[@class="pt-0 font-medium mr-3 text-[28px] leading-9 text-black "]/text()')
        price = price[0].strip() if price else None
    except:
        price = None

    try:
        currency = tree.xpath('//span[@class="text-base font-medium leading-5"]/text()')
        currency = currency[0].strip() if currency else None
    except:
        currency = None
    try:
        rating = tree.xpath('//span[@class="mr-[5px] text-5xl font-medium leading-9 text-neutral-800")]//text()')
        rating = " ".join([d.strip() for d in rating if d.strip()])
    except:
        rating = None

    try:
        description = tree.xpath('//span[@class="text-base font-normal not-italic leading-6 text-black")]//text()')
        description = " ".join([d.strip() for d in description if d.strip()])
    except:
        description = None

    return {
        "url": url,
        "title": title,
        "price": price,
        "currency": currency,
        "rating": rating,
        "description": description
    }

if __name__ == "__main__":
    results = []

    # Collect all product URLs from output JSON
    all_products = []
    for subcat, urls in crawled_data.get("products", {}).items():
        all_products.extend(urls)

    print(f"[INFO] Found {len(all_products)} products to parse.")

    for url in all_products[:20]:  # limit to first 20 for testing
        data = parse_product(url)
        if data:
            results.append(data)

    # Save results
    with open("cvs_products.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("[INFO] Saved cvs_products.json")
