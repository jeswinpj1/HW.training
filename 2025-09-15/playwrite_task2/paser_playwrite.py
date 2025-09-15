# parser_xpath.py
from playwright.sync_api import sync_playwright
import json, os, time

OUTPUT_DIR = "output"
LINKS_FILE = os.path.join(OUTPUT_DIR, "links.jsonl")
PARSED_FILE = os.path.join(OUTPUT_DIR, "parsed.jsonl")

def extract_text(page, xpath_expr):
    el = page.query_selector(xpath_expr)
    return el.inner_text().strip() if el else ""

def extract_unique_id(url):
    return url.split("-")[-1].replace("/", "")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    with open(PARSED_FILE, "w", encoding="utf-8") as out_f:
        with open(LINKS_FILE, "r", encoding="utf-8") as in_f:
            for line in in_f:
                record = json.loads(line)
                for prod_url in record.get("product_urls", []):
                    try:
                        print("Parsing:", prod_url)
                        page.goto(prod_url, timeout=60000)
                        page.wait_for_load_state("networkidle")
                        time.sleep(1)

                        data = {
                            "url": prod_url,
                            "main_category": record["main_category"],
                            "sub_category": record["sub_category"],
                            "title": extract_text(page, "//h1"),
                            "price": extract_text(page, "//*[contains(@class,'price')]"),
                            "unique_id": extract_unique_id(prod_url),
                            "description": extract_text(page, "//div[contains(@class,'description')] | //p"),
                            "location": extract_text(page, "//*[contains(@class,'location')]"),
                        }

                        out_f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    except Exception as e:
                        print("Error parsing", prod_url, e)

    browser.close()

print(f"Parsing finished. Results in {PARSED_FILE}")
