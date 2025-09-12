# import asyncio
# import json
# from playwright.async_api import async_playwright

# START_URL = "https://www.olx.in/en-in/kerala_g2001160/for-sale-houses-apartments_c1725"
# OUTPUT_FILE = "crawler_urls.json"
# MAX_PAGES = 3  # limit for testing

# # A desktop Chrome User-Agent (matches what OLX expects)
# UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"


# async def crawl_olx():
#     urls = []

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)  # debug mode first
#         context = await browser.new_context(user_agent=UA)
#         page = await context.new_page()

#         current_page = 1
#         url = START_URL

#         while current_page <= MAX_PAGES:
#             print(f"[INFO] Crawling page {current_page}: {url}")

#             await page.goto(url, timeout=60000, wait_until="domcontentloaded")

#             # Small wait to ensure elements load
#             await page.wait_for_timeout(3000)

#             # Collect listing links
#             links = await page.locator("//a[contains(@href,'/item/')]").evaluate_all(
#                 "els => els.map(el => el.href)"
#             )
#             for link in links:
#                 if link not in urls:
#                     urls.append(link)

#             print(f"[INFO] Collected {len(urls)} URLs so far...")

#             # Go to next page
#             next_btn = page.locator("//a[contains(@rel,'next')]")
#             if await next_btn.count() > 0:
#                 next_url = await next_btn.get_attribute("href")
#                 if not next_url:
#                     break
#                 url = next_url
#                 current_page += 1
#             else:
#                 break

#         await browser.close()

#     # Save URLs
#     with open(OUTPUT_FILE, "w") as f:
#         json.dump([{"url": u} for u in urls], f, indent=2)

#     print(f"[DONE] Saved {len(urls)} URLs to {OUTPUT_FILE}")


# if __name__ == "__main__":
#     asyncio.run(crawl_olx())


import asyncio
import json
import random
from pymongo import MongoClient
from playwright.async_api import async_playwright

START_URL = "https://www.olx.in/en-in/kerala_g2001160/for-sale-houses-apartments_c1725"
OUTPUT_FILE = "crawler1_urls.json"
USER_AGENTS_FILE = "/home/user/HW.training/2025-09-12/user_agents.txt"

MAX_PAGES = 5  # adjust as needed


def load_user_agents(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


async def crawl_olx():
    user_agents = load_user_agents(USER_AGENTS_FILE)
    if not user_agents:
        print("[ERROR] No user agents found in file.")
        return

    # MongoDB connection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["playwright_olx_db"]
    collection = db["crawler_urls"]

    all_urls = []

    async with async_playwright() as p:
        # Run non-headless to avoid bot detection
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-http2",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-gpu",
            ]
        )

        for page_num in range(1, MAX_PAGES + 1):
            url = f"{START_URL}?page={page_num}"
            user_agent = random.choice(user_agents)

            context = await browser.new_context(
                user_agent=user_agent,
                viewport={"width": 1366, "height": 768},
                java_script_enabled=True,
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                }
            )
            page = await context.new_page()

            print(f"[INFO] Crawling page {page_num}: {url} with UA: {user_agent}")

            success = False
            for attempt in range(3):  # retry 3 times
                try:
                    await page.goto(url, timeout=90000, wait_until="networkidle")
                    success = True
                    break
                except Exception as e:
                    print(f"[WARN] Attempt {attempt+1} failed: {e}")
                    await asyncio.sleep(5)

            if not success:
                print(f"[ERROR] Skipping page {page_num} after 3 retries.")
                await context.close()
                continue

            # Extract product links
            links = await page.eval_on_selector_all(
                "a",
                "elements => elements.map(el => el.href).filter(href => href.includes('/item/'))"
            )

            if not links:
                print(f"[WARN] No links found on page {page_num}.")
            else:
                for link in links:
                    if link not in all_urls:
                        all_urls.append(link)
                        collection.update_one(
                            {"url": link},
                            {"$set": {"url": link}},
                            upsert=True
                        )
                print(f"[INFO] Found {len(links)} URLs on page {page_num}")

            await context.close()

        await browser.close()

    # Save to JSON
    with open(OUTPUT_FILE, "w") as f:
        json.dump([{"url": u} for u in all_urls], f, indent=2)

    print(f"[DONE] Saved {len(all_urls)} URLs to {OUTPUT_FILE} & MongoDB")


if __name__ == "__main__":
    asyncio.run(crawl_olx())
