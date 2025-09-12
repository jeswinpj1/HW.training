

import subprocess
from lxml import html
import json

API_KEY = "504eeef7c076dfcf401adae86875886d"
START_URL = "https://www.olx.in/en-in/kerala_g2001160/for-sale-houses-apartments_c1725"
OUTPUT_FILE = "crawler_urls.json"

def crawl_olx_with_curl(max_pages=5):
    urls = []
    page = 1

    while page <= max_pages:
        print(f"[INFO] Crawling page {page}...")

        proxied_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={START_URL}?page={page}&country_code=IN"
        # Call curl
        result = subprocess.run(
            ["curl", "-s", proxied_url],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"[ERROR] curl failed on page {page}")
            break

        tree = html.fromstring(result.stdout)
        links = tree.xpath("//a[contains(@href,'/item/')]/@href")
        if not links:
            break

        for link in links:
            full_url = "https://www.olx.in" + link if link.startswith("/") else link
            if full_url not in urls:
                urls.append(full_url)

        page += 1

    # Save URLs
    with open(OUTPUT_FILE, "w") as f:
        json.dump([{"url": u} for u in urls], f, indent=2)

    print(f"[DONE] Saved {len(urls)} URLs to {OUTPUT_FILE}")

if __name__ == "__main__":
    crawl_olx_with_curl()

