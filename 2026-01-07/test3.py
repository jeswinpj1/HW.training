import requests
import time
import json
import random
from parsel import Selector

INPUT_FILE = "/home/user/HW.training/product_urls.json"
OUTPUT_FILE = "mueller_products.json"

LIMIT = 110
MAX_RETRIES = 5

# ========= PROXY =========
PROXY = {
    "http": "http://liyrhwyo:ltar0vrszrau@142.111.48.253:7030",
    "https": "http://liyrhwyo:ltar0vrszrau@142.111.48.253:7030",
}

# ========= HEADERS =========
HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.mueller.at/",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.mueller.at/",
    }
]

# ========= COOKIES =========
COOKIES_LIST = [
    {
        "__Secure-CDNCID": "a3QR1q1wiv7yKyG48yHYWe5NnBfuE+YqtwsVeqFriSXCzeLG19rNRpLWRtaMqAcT2EQHaKAq6TwoFfCJoilzZrGtwEJY9paR9e7dlag8YlrTQyFqGZWQrdNaP8HbWYE1",
        "_ga": "GA1.1.1353725261.1767765760",
        "_gcl_au": "1.1.148244020.1767765760",
    },
    {
        "_fbp": "fb.1.1767765760392.62990823565534839",
        "trbo_usr": "5ee4339e54547f60f245899a92c9ccd4",
        "_pm3pc": "1",
    },
    {
        "INGRESSCOOKIE": "1767798757.332.1681.347482|2287d48963360908c030ff2bb9f3cc00",
        "_ga_HKQ81S5B0H": "GS2.1.s1767797702$o7$g1$t1767799093$j60$l0$h2055152784",
    }
]

# ========= LOAD URLS =========
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    product_urls = json.load(f)

results = []

# ========= MAIN LOOP =========
for idx, url in enumerate(product_urls[:LIMIT], 1):
    print(f"\n[{idx}/{LIMIT}] Fetching: {url}")
    success = False

    for attempt in range(1, MAX_RETRIES + 1):
        headers = random.choice(HEADERS_LIST)
        cookies = random.choice(COOKIES_LIST)

        session = requests.Session()
        session.headers.update(headers)
        session.cookies.update(cookies)

        try:
            r = session.get(
                url,
                proxies=PROXY,
                timeout=40,
                allow_redirects=True
            )

            if r.status_code == 403:
                print(f"403 Forbidden (Attempt {attempt}/{MAX_RETRIES})")
                time.sleep(random.uniform(2, 4))
                continue

            if r.status_code != 200:
                print(f"HTTP {r.status_code}")
                break

            sel = Selector(r.text)

            # ========= PARSE =========
            details = {}
            for row in sel.xpath('//table[contains(@class,"specifications-table")]//tr'):
                k = row.xpath('./td[1]//text()').get(default="").strip()
                v = row.xpath('./td[2]//text()').get(default="").strip()
                if k:
                    details[k] = v
            hazard_signal = sel.xpath('//div[@id="gefahrenhinweis"]//span[contains(@class,"warning-signalword")]/text()').get(default="")
            hazard_text = sel.xpath('//div[@id="gefahrenhinweis"]//span[not(contains(@class,"warning-signalword"))]/text()').get(default="")
            safety_text = sel.xpath('//div[@id="warnhinweis"]//span/text()').get(default="")

            description = " ".join(sel.xpath(
                '//div[contains(@class,"accordion-entry__contents")]//p//text() | '
                '//div[contains(@class,"accordion-entry__contents")]//li//text()'
            ).getall()).strip()

            item = {
            "product_url": url,
            "brand_name": sel.xpath('//a[contains(@class,"product-info__brand")]/@href').get(default="").split("/")[-2].replace("-", " ").upper(),
            "brand_url": sel.xpath('//a[contains(@class,"product-info__brand")]/@href').get(),
            "product_name": sel.xpath('//h1/text()').get(),
            "article_number": sel.xpath('//syndigo-powerpage/@pageid').get(),
            "price": sel.xpath('//span[contains(@class,"h1 h2-desktop-only")]/text()').get(),
            "strike_price": sel.xpath('//span[contains(@class,"strike-price-value")]/text()').get(),
            "base_price": sel.xpath('//div[contains(@class,"base-price")]//span[1]/text()').get(),
            "discount_text": sel.xpath('//span[contains(@class,"price-discount")]/text()').get(),
            "content_ml": details.get("Inhalt"),
            "description": description,
            "delivery_home": sel.xpath('//div[contains(@title,"Lieferung nach Hause")]//li/text()').getall(),
            "delivery_store": sel.xpath('//div[contains(@title,"Lieferung in die Filiale")]//li/text()').getall(),
            "artikel_details": details,          # add table as key-value
            "gefahrenhinweis": {"signal": hazard_signal, "text": hazard_text},
            "sicherheitshinweis": safety_text
        }

            results.append(item)

            # ========= SAVE AFTER EACH =========
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print("Success")
            success = True
            time.sleep(random.uniform(2.5, 4.5))
            break

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)

    if not success:
        print(f"Skipped after {MAX_RETRIES} attempts")

print(f"\n DONE — {len(results)} products saved")
