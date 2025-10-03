# parser_with_cookies.py
from playwright.sync_api import sync_playwright
from pymongo import MongoClient, ReturnDocument
import json
import time
import random
import os
import re

# ---------- CONFIG ----------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "pap"
URL_COLLECTION = "property_urls"
DATA_COLLECTION = "property_details"

COOKIES_FILE = "cookies.json"  # produced by save_cookies.py
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

# Optional proxy
PROXY = None  # {"server": "http://YOUR_PROXY_IP:PORT"} or None

RF_RE = re.compile(r"(?:Réf(?:\.|erence)?[:\s]*)([A-Za-z0-9\-_/]+)", re.IGNORECASE)

# ---------- DB ----------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
url_collection = db[URL_COLLECTION]
data_collection = db[DATA_COLLECTION]

# ---------- Helpers ----------
def load_cookies():
    if not os.path.exists(COOKIES_FILE):
        raise FileNotFoundError(f"{COOKIES_FILE} not found. Run save_cookies.py first.")
    with open(COOKIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def cookies_expiry_warning(cookies):
    now = time.time()
    expired = [c for c in cookies if c.get("expires", -1) != -1 and c["expires"] < now]
    if expired:
        print(f"[WARN] {len(expired)} cookie(s) already expired — re-run save_cookies.py")
    else:
        soon = [c for c in cookies if c.get("expires", float("inf")) - now < 3600*24*3]
        if soon:
            print(f"[INFO] {len(soon)} cookie(s) will expire within 3 days — plan to refresh soon")

def human_wait(min_s=0.6, max_s=1.6):
    time.sleep(random.uniform(min_s, max_s))

def random_mouse_movements(page, moves=5):
    viewport = page.viewport_size or {"width": 1200, "height": 800}
    w, h = viewport["width"], viewport["height"]
    for _ in range(moves):
        x = random.randint(int(w*0.1), int(w*0.9))
        y = random.randint(int(h*0.1), int(h*0.9))
        page.mouse.move(x, y, steps=random.randint(10, 25))
        human_wait(0.05, 0.2)

def random_scroll(page):
    """Scroll down a random amount to simulate reading."""
    page.evaluate("window.scrollBy(0, window.innerHeight * Math.random())")
    human_wait(0.5, 1.2)

def extract_rf(text):
    """Return the RF token extracted from a text, or 'N/A'."""
    if not text:
        return "N/A"
    m = RF_RE.search(text)
    return m.group(1).strip() if m else text.strip()

def save_property_details_upsert(data):
    """Upsert the property details with a scraped_at timestamp."""
    data_to_set = {
        "title": data.get("title", "N/A"),
        "price": data.get("price", "N/A"),
        "rfno": data.get("rfno", "N/A"),
        "scraped_at": time.time()
    }
    res = data_collection.find_one_and_update(
        {"url": data["url"]},
        {"$set": data_to_set, "$setOnInsert": {"first_seen": time.time()}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    if res:
        print(f"[UPSERTED] {data['url']}")

# Basic stealth injection
STEALTH_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.__proto__.query = function(parameters) {
  if (parameters && parameters.name === 'notifications') {
    return Promise.resolve({ state: Notification.permission });
  }
  return originalQuery(parameters);
};
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
"""

# ---------- Parsing logic ----------
def parse_property_page(page, url, retries=3):
    if not "/annonces/" in url:
        print(f"[SKIP-NON-LISTING] {url}")
        return

    for attempt in range(1, retries+1):
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            human_wait(1.0, 2.2)

            # Random mouse and scroll to avoid detection
            random_mouse_movements(page, moves=3)
            random_scroll(page)

            title_text = page.title().strip()
            if "www.pap.fr" in title_text.lower():
                print(f"[BLOCKED] {url} -> title: {title_text} (attempt {attempt}/{retries})")
                human_wait(2, 4)
                continue  # retry

            title_el = page.query_selector("//h1")
            title = title_el.inner_text().strip() if title_el else "N/A"

            price_el = page.query_selector("//span[contains(@class,'price') or contains(@class,'item-price')]")
            if not price_el:
                price_el = page.query_selector("//div[contains(@class,'price')]//span")
            price = price_el.inner_text().strip() if price_el else "N/A"

            rf_el = page.query_selector("//*[contains(text(),'Réf') or contains(text(),'Référence') or contains(text(),'Réf.')]")
            rf_raw = rf_el.inner_text().strip() if rf_el else ""
            rfno = extract_rf(rf_raw) if rf_raw else "N/A"

            data = {"url": url, "title": title, "price": price, "rfno": rfno}
            save_property_details_upsert(data)
            human_wait(0.8, 1.8)
            return  # success

        except Exception as e:
            print(f"[ERROR] parsing {url}: {e} (attempt {attempt}/{retries})")
            human_wait(1.0, 2.5)

    print(f"[FAIL] {url} after {retries} attempts")

# ---------- Main ----------
def main():
    cookies = load_cookies()
    cookies_expiry_warning(cookies)

    urls_cursor = url_collection.find()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=80, proxy=PROXY)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1200, "height": 800},
            java_script_enabled=True
        )

        try:
            context.add_cookies(cookies)
            print(f"[INFO] Loaded {len(cookies)} cookies into context")
        except Exception as ex:
            print(f"[WARN] Could not add cookies: {ex}")

        page = context.new_page()
        page.add_init_script(STEALTH_SCRIPT)

        for item in urls_cursor:
            url = item.get("url")
            if not url:
                continue
            human_wait(0.5, 1.4)
            random_mouse_movements(page, moves=2)
            parse_property_page(page, url, retries=3)

        print("[DONE] Finished all URLs")
        browser.close()

if __name__ == "__main__":
    main()
