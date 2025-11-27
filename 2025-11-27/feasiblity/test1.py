import requests
from parsel import Selector
import json
import time

BASE_URL = "https://www.emlakjet.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
}

session = requests.Session()
session.headers.update(HEADERS)


# ---------------------------------------------------------
# Utility: GET HTML page
# ---------------------------------------------------------
def fetch(url):
    try:
        print("[FETCH]", url)
        r = session.get(url, timeout=20)
        r.raise_for_status()
        return Selector(text=r.text)
    except Exception as e:
        print("[ERROR] Fetch:", url, str(e))
        return None


# ---------------------------------------------------------
# STEP 1 — Extract all MAIN + SUB categories
# ---------------------------------------------------------
# ---------------------------------------------------------
# STEP 1 — Extract all MAIN + SUB categories
# ---------------------------------------------------------
def extract_categories():
    homepage = fetch(BASE_URL)
    if homepage is None:
        return []

    categories = []

    main_nodes = homepage.xpath("//ul[contains(@class,'styles_menu')]//li")

    for m in main_nodes:
        main_name = m.xpath(".//div/text()[1]").get(default="").strip()
        if not main_name:
            continue

        # --------------------
        # Normal categories
        # --------------------
        subcats = []
        sub_nodes = m.xpath(".//ul/li/a")

        for s in sub_nodes:
            sub_name = s.xpath("text()").get("").strip()
            sub_url = s.xpath("@href").get("")

            if sub_url.startswith("/"):
                sub_url = BASE_URL + sub_url

            subcats.append({
                "sub_name": sub_name,
                "sub_url": sub_url,
                "subsub": []        # always include field
            })
        
        # Add the main category and its subcategories to the list
        categories.append({
            "main_name": main_name,
            "subcategories": subcats
        })


        # --------------------------------------------------------
        # SPECIAL CASE → Hizmetlerimiz (Our Services) - Process sub-sub *AFTER* adding main
        # --------------------------------------------------------
        if main_name.lower().startswith("hizmet"):
            # For each subcategory under Hizmetlerimiz
            for sub in categories[-1]["subcategories"]: # Use the subcats just added

                print("[SCAN SUB-SUB] =>", sub["sub_url"])
                page = fetch(sub["sub_url"])
                if not page:
                    continue

                # Scan grid boxes inside THIS subcategory page
                nodes = page.xpath("//div[contains(@class,'sc-bdVaJa')]//a")

                subsub_list = []
                for n in nodes:
                    name = n.xpath(".//p[@class='_1Rlw-b']/text()").get("").strip()
                    url = n.xpath("@href").get("")

                    if url.startswith("/"):
                        url = BASE_URL + url

                    if name and url:
                        subsub_list.append({
                            "subsub_name": name,
                            "subsub_url": url
                        })

                sub["subsub"] = subsub_list

    # --------------------------------------------------------
    # FINAL FIX: RETURN CATEGORIES ONLY AFTER THE WHOLE LOOP IS DONE
    # --------------------------------------------------------
    return categories

# ---------------------------------------------------------
# STEP 2 — From a category page, collect product URLs using SAYFA pagination
# ---------------------------------------------------------
def extract_product_urls(cat_url):
    product_urls = set()
    next_page = cat_url  # Start here

    while next_page:

        sel = fetch(next_page)
        if sel is None:
            break

        # -----------------------
        # PRODUCT URL extraction
        # -----------------------
        items = sel.xpath("//a[contains(@class,'styles_wrapper')]//@href")

        if not items:
            print("[NO PRODUCTS] Ending...")
            break

        for href in items.getall():
            if href.startswith("/"):
                href = BASE_URL + href
            product_urls.add(href)

        print(f"[FOUND PRODUCTS] {len(items)} on page")

        # -----------------------
        # PAGINATION: next page link
        # -----------------------
        next_page_href = sel.xpath(
            "//ul[contains(@class,'styles_list')]//li[@class='styles_rightArrow__Kn4kW']/a/@href"
        ).get()

        if not next_page_href:
            print("[NO NEXT PAGE] Ending pagination.")
            break

        # Build next page full URL
        if next_page_href.startswith("/"):
            next_page = BASE_URL + next_page_href
        else:
            next_page = next_page_href

        time.sleep(1)

    return list(product_urls)


# ---------------------------------------------------------
# MAIN — Build full output JSON
# ---------------------------------------------------------
def run():
    data = []

    print("\n[STEP 1] Extracting categories...")
    categories = extract_categories()

    print(f"Found {len(categories)} Main Categories")

    for cat in categories:

        for sub in cat["subcategories"]:

            # ---------------------------------------------------------
            # CASE 1 — NORMAL CATEGORY (no sub-sub)
            # ---------------------------------------------------------
            if not sub["subsub"]:

                print(f"\n[STEP 2] Crawling: {cat['main_name']} -> {sub['sub_name']}")
                urls = extract_product_urls(sub["sub_url"])

                data.append({
                    "main_category": cat["main_name"],
                    "sub_category": sub["sub_name"],
                    "sub_url": sub["sub_url"],
                    "product_urls": urls
                })

            # ---------------------------------------------------------
            # CASE 2 — Hizmetlerimiz → sub → sub-sub
            # ---------------------------------------------------------
            else:
                for s2 in sub["subsub"]:
                    print(f"\n[STEP 2] Crawling: {cat['main_name']} -> {sub['sub_name']} -> {s2['subsub_name']}")

                    urls = extract_product_urls(s2["subsub_url"])

                    data.append({
                        "main_category": cat["main_name"],
                        "sub_category": sub["sub_name"],
                        "sub_sub_category": s2["subsub_name"],
                        "sub_sub_url": s2["subsub_url"],
                        "product_urls": urls
                    })

    # -------------------------------------------------------------
    # SAVE TO JSON
    # -------------------------------------------------------------
    with open("emlakjet_product_urls.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n✔ FINISHED — Saved: emlakjet_product_urls.json")


if __name__ == "__main__":
    run()
