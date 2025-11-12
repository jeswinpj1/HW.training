import requests
from parsel import Selector
import json
import time

# Base URL and headers/cookies
base_url = "https://classiccars.com/listings/find/until-1990"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.classiccars.com/",
    "Connection": "keep-alive"
}

cookies = {
    "IDE": "AHWqTUkOeRTNh07YhdhUD176dl3is_181CUVbLfHUzDhrBJt7Oj6pRD_hha5KKGkPu4",
    "DSID": "AEhM4MfwkxlssRFoHWRFN-HIBBA0Wkv21MqEMJpvO5mjya5kQgqh-mwVXswfNp_mDP-PPAxaeXf2Cz6VCB9lYuu63G8n82egqk3KiKNHSUF3P50Ru_PyoJfjlqKvOrKy8MHrxOHxkDrxnMRMtGTTdgc0NwGGigl0mceTqcbl47u8FfIsyI1zCjQ9Tt_sB6JVilPfJ1xyXgJygkl7eNamD8IaJthw2YZj4l_T-0NMLJdWedMDsqcCkvrXzJY4K7rQn9Y5N1MKRjjJJkeRDCoh6m7uKLGAa4FyzzTANStQDnJ7i_1y8TbR4TY"
}

all_urls = []
page = 1

while True:
    print(f"Fetching page {page}...")
    url = f"{base_url}?p={page}"
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        print(f"Failed to fetch page {page}, status code: {response.status_code}")
        break

    sel = Selector(text=response.text)

    # Extract car listing URLs
    links = sel.xpath('//a[@class="d-block w100 dark-link"]/@href').getall()
    if not links[:3]:
        print("No more listings found, stopping.")
        break

    all_urls.extend([f"https://classiccars.com{l}" for l in links])

    # Check if next page exists
    next_page = sel.xpath('//li[@class="active "]/following-sibling::li[1]/a/@href').get()
    if not next_page:
        break

    page += 1
    time.sleep(0.5)  # polite delay

# Save to JSON
with open("classiccars_until1990_urls.json", "w") as f:
    json.dump(all_urls, f, indent=4)

print(f"Total URLs collected: {len(all_urls)}")
