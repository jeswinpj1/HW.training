import asyncio
import json
from playwright.async_api import async_playwright

INPUT_FILE = "crawler1_urls.json"
OUTPUT_FILE = "olx_listings.json"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"


async def parse_listing(browser, url):
    context = await browser.new_context(
        user_agent=UA,
        ignore_https_errors=True,  # helps with ERR_HTTP2_PROTOCOL_ERROR
    )
    page = await context.new_page()

    try:
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        title = await page.locator("//h1").inner_text(timeout=5000)

        price = ""
        price_el = page.locator("//span[contains(@class,'T8y-z')]")
        if await price_el.count() > 0:
            price = await price_el.first.inner_text()

        location = ""
        loc_el = page.locator("//span[contains(@class,'_1RkZP')]")
        if await loc_el.count() > 0:
            location = await loc_el.first.inner_text()

        description = ""
        desc_el = page.locator("//div[@data-aut-id='itemDescriptionContent']")
        if await desc_el.count() > 0:
            description = await desc_el.first.inner_text()

        await context.close()
        return {
            "url": url,
            "title": title.strip(),
            "price": price.strip(),
            "location": location.strip(),
            "description": description.strip(),
        }

    except Exception as e:
        print(f"[WARN] Could not parse {url}: {e}")
        await context.close()
        return None


async def main():
    with open(INPUT_FILE) as f:
        urls = [entry["url"] for entry in json.load(f)]

    listings = []

    async with async_playwright() as p:
        # Try Chromium first
        browser = await p.chromium.launch(headless=False)
        for idx, url in enumerate(urls, 1):
            print(f"[INFO] Processing {idx}/{len(urls)}: {url}")
            listing = await parse_listing(browser, url)

            if not listing:
                # Retry with Firefox
                print(f"[RETRY] Retrying with Firefox: {url}")
                firefox = await p.firefox.launch(headless=False)
                listing = await parse_listing(firefox, url)
                await firefox.close()

            if listing:
                listings.append(listing)

        await browser.close()

    with open(OUTPUT_FILE, "w") as f:
        json.dump(listings, f, indent=2)

    print(f"[DONE] Saved {len(listings)} listings to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
