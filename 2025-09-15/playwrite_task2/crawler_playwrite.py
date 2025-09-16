
# import asyncio
# import json
# import os
# import re
# import time
# from playwright.async_api import async_playwright

# START_URL = "https://www.dubizzle.com.bh/en"
# USER_AGENT = "PolitePythonCrawler/1.0 (+your_email@example.com)"
# MAX_PAGES = 2     # keep small while testing
# DELAY_SEC = 3      # polite delay

# OUTPUT_DIR = "output"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# CATEGORY_SELECTOR = "a[href*='/en/']:not([href*='login']):not([href^='mailto:'])"
# PRODUCT_SELECTOR = "a[href*='/item-'], a[href*='/listing-'], a[href*='/ad/']"

# async def crawl():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         context = await browser.new_context(user_agent=USER_AGENT)
#         page = await context.new_page()

#         to_visit = [START_URL]
#         visited = set()
#         categories = set()
#         subcategories = set()
#         product_urls = set()

#         while to_visit and len(visited) < MAX_PAGES:
#             url = to_visit.pop(0)
#             if url in visited:
#                 continue
#             try:
#                 print(f"Visiting: {url}")
#                 await page.goto(url, wait_until="networkidle", timeout=30000)
#                 visited.add(url)

#                 # collect category/subcategory links
#                 anchors = await page.eval_on_selector_all(
#                     CATEGORY_SELECTOR, "els => els.map(a => a.href)"
#                 )
#                 for href in anchors:
#                     if href.startswith("http") and "/en/" in href:
#                         if href.count("/") <= 5:
#                             categories.add(href)
#                         else:
#                             subcategories.add(href)
#                         if href not in visited and href not in to_visit:
#                             to_visit.append(href)

#                 # collect product links
#                 prod_links = await page.eval_on_selector_all(
#                     "a[href]", "els => els.map(a => a.href)"
#                 )
#                 for href in prod_links:
#                     if re.search(r"/(item|listing|ad)[\-/\d\w]*", href):
#                         product_urls.add(href.split("#")[0])

#                 print(f"Visited {len(visited)} pages. Sleeping {DELAY_SEC}s...")
#                 time.sleep(DELAY_SEC)

#             except Exception as e:
#                 print("Error visiting", url, e)
#                 time.sleep(1)

#         # save results
#         with open(os.path.join(OUTPUT_DIR, "categories.json"), "w") as f:
#             json.dump(list(categories), f, indent=2)
#         with open(os.path.join(OUTPUT_DIR, "subcategories.json"), "w") as f:
#             json.dump(list(subcategories), f, indent=2)
#         with open(os.path.join(OUTPUT_DIR, "product_urls.json"), "w") as f:
#             json.dump(list(product_urls), f, indent=2)

#         await browser.close()
#         print("Done. Results saved to ./output/*.json")

# if __name__ == "__main__":
#     asyncio.run(crawl())




import asyncio
import json
import os
import re
import time
import cloudscraper
from playwright.async_api import async_playwright

START_URL = "https://www.dubizzle.com.bh/en"
USER_AGENT = "PolitePythonCrawler/1.0 (+your_email@example.com)"
MAX_PAGES = 2     # keep small while testing
DELAY_SEC = 3     # polite delay

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CATEGORY_SELECTOR = "a[href*='/en/']:not([href*='login']):not([href^='mailto:'])"
PRODUCT_SELECTOR = "a[href*='/item-'], a[href*='/listing-'], a[href*='/ad/']"

# ----------------- NEW: solve Cloudflare ----------------- #
def get_cloudflare_cookies(url):
    scraper = cloudscraper.create_scraper()
    res = scraper.get(url)
    print("[cloudscraper] status:", res.status_code)
    return scraper.cookies.get_dict()

# ----------------- MAIN CRAWLER ----------------- #
async def crawl():
    # Step 1: solve Cloudflare
    cookies = get_cloudflare_cookies(START_URL)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent=USER_AGENT)

        # Step 2: add cookies into Playwright context
        await context.add_cookies([
    {
        "name": k,
        "value": v,
        "domain": ".dubizzle.com.bh",
        "path": "/",
    }
    for k, v in cookies.items()
        ])


        page = await context.new_page()

        to_visit = [START_URL]
        visited = set()
        categories = set()
        subcategories = set()
        product_urls = set()

        while to_visit and len(visited) < MAX_PAGES:
            url = to_visit.pop(0)
            if url in visited:
                continue
            try:
                print(f"Visiting: {url}")
                await page.goto(url, wait_until="networkidle", timeout=30000)
                visited.add(url)

                # collect category/subcategory links
                anchors = await page.eval_on_selector_all(
                    CATEGORY_SELECTOR, "els => els.map(a => a.href)"
                )
                for href in anchors:
                    if href.startswith("http") and "/en/" in href:
                        if href.count("/") <= 5:
                            categories.add(href)
                        else:
                            subcategories.add(href)
                        if href not in visited and href not in to_visit:
                            to_visit.append(href)

                # collect product links
                prod_links = await page.eval_on_selector_all(
                    "a[href]", "els => els.map(a => a.href)"
                )
                for href in prod_links:
                    if re.search(r"/(item|listing|ad)[\-/\d\w]*", href):
                        product_urls.add(href.split("#")[0])

                print(f"Visited {len(visited)} pages. Sleeping {DELAY_SEC}s...")
                time.sleep(DELAY_SEC)

            except Exception as e:
                print("Error visiting", url, e)
                time.sleep(1)

        # save results
        with open(os.path.join(OUTPUT_DIR, "categories.json"), "w") as f:
            json.dump(list(categories), f, indent=2)
        with open(os.path.join(OUTPUT_DIR, "subcategories.json"), "w") as f:
            json.dump(list(subcategories), f, indent=2)
        with open(os.path.join(OUTPUT_DIR, "product_urls.json"), "w") as f:
            json.dump(list(product_urls), f, indent=2)

        await browser.close()
        print("Done. Results saved to ./output/*.json")

if __name__ == "__main__":
    asyncio.run(crawl())
