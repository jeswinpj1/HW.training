import requests
from parsel import Selector
import time
from lxml import html

BASE_URL = "https://www.emlakjet.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
}

session = requests.Session()
session.headers.update(HEADERS)

# ============================
# CRAWLER: Extract product URLs
# ============================
def fetch(url):
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        return Selector(text=r.text)
    except Exception as e:
        print(f"[ERROR] Fetch {url} -> {e}")
        return None

def extract_categories():
    homepage = fetch(BASE_URL)
    if not homepage:
        return []

    categories = []
    main_nodes = homepage.xpath("//ul[contains(@class,'styles_menu')]//li")

    for m in main_nodes:
        main_name = m.xpath(".//div/text()[1]").get(default="").strip()
        if not main_name:
            continue

        subcats = []
        for s in m.xpath(".//ul/li/a"):
            sub_name = s.xpath("text()").get("").strip()
            sub_url = s.xpath("@href").get("")
            if sub_url.startswith("/"):
                sub_url = BASE_URL + sub_url
            subcats.append({"sub_name": sub_name, "sub_url": sub_url, "subsub": []})
        categories.append({"main_name": main_name, "subcategories": subcats})

        # Special case for Hizmetlerimiz
        if main_name.lower().startswith("hizmet"):
            for sub in categories[-1]["subcategories"]:
                page = fetch(sub["sub_url"])
                if not page:
                    continue
                nodes = page.xpath("//div[contains(@class,'sc-bdVaJa')]//a")
                subsub_list = []
                for n in nodes:
                    name = n.xpath(".//p[@class='_1Rlw-b']/text()").get("").strip()
                    url = n.xpath("@href").get("")
                    if url.startswith("/"):
                        url = BASE_URL + url
                    if name and url:
                        subsub_list.append({"subsub_name": name, "subsub_url": url})
                sub["subsub"] = subsub_list
    return categories

def extract_product_urls(cat_url):
    urls = set()
    next_page = cat_url
    while next_page:
        sel = fetch(next_page)
        if not sel:
            break
        items = sel.xpath("//a[contains(@class,'styles_wrapper')]//@href")
        for href in items.getall():
            if href.startswith("/"):
                href = BASE_URL + href
            urls.add(href)
        next_page_href = sel.xpath("//ul[contains(@class,'styles_list')]//li[@class='styles_rightArrow__Kn4kW']/a/@href").get()
        if not next_page_href:
            break
        next_page = BASE_URL + next_page_href if next_page_href.startswith("/") else next_page_href
        time.sleep(1)
    return list(urls)

# ============================
# PARSER: Extract product details
# ============================
def scrape_property(url):
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        sel = html.fromstring(r.text)

        # Title
        title = sel.xpath('//h1[contains(@class,"styles_title")]//text()')
        title = " ".join(t.strip() for t in title if t.strip()) or None

        # Price
        price = sel.xpath('//span[contains(@class,"styles_price")]//text()')
        price = " ".join(p.strip() for p in price if p.strip()) or None

        # Images
        images = sel.xpath('//div[contains(@class,"styles_inner__")]//img/@src')
        images = list({img for img in images if img})

        return {"url": url, "title": title, "price": price, "images": images, "success": True}

    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return {"url": url, "title": None, "price": None, "images": [], "success": False, "error": str(e)}


# -------- FINDINGS --------
#  Some listings may not have price or images.
#  'Hizmetlerimiz' category has sub-sub categories that are captured.


