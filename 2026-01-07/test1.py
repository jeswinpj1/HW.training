import requests
from parsel import Selector

# URL of the Parfümerie page
url = "https://www.mueller.at/c/parfuemerie/"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "referer": "https://www.mueller.at/",
}

# Use the cookie you provided
cookies = {
    "__Secure-CDNCID": "a3QR1q1wiv7yKyG48yHYWe5NnBfuE+YqtwsVeqFriSXCzeLG19rNRpLWRtaMqAcT2EQHaKAq6TwoFfCJoilzZrGtwEJY9paR9e7dlag8YlrTQyFqGZWQrdNaP8HbWYE1",
    "SearchCollectorSession": "vfBwzdk",
    "INGRESSCOOKIE": "1767765756.872.1681.677435|2287d48963360908c030ff2bb9f3cc00",
    "_gcl_au": "1.1.148244020.1767765760",
    "_ga": "GA1.1.1353725261.1767765760",
    "_fbp": "fb.1.1767765760392.62990823565534839",
    "trbo_usr": "5ee4339e54547f60f245899a92c9ccd4",
    "emos_jcvid": "AZuXDNraxddZHgKdw33IUtwt8QG6fvjZ:1:0:0:0:true:1",
    "_pm3pc": "1",
    "trbo_ac-visitor-id": "52b2a959-0fd9-4620-a7f8-055f63918842",
    "trbo_ac-welcome-message-actively-closed": "2026-01-07T06%3A03%3A33.029Z",
    # Add other cookies from your string as needed
}

# Fetch the page
response = requests.get(url, headers=headers, cookies=cookies)

if response.status_code != 200:
    print("Failed to fetch page:", response.status_code)
    exit()

# Parse the HTML
sel = Selector(text=response.text)

# XPath for category blocks
category_blocks = sel.xpath('//div[contains(@class,"banner_component_headline_headline__wkTJS")]')

# Save to file
output_file = "parfuemerie_categories.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for block in category_blocks:
        # Extract the link
        link = block.xpath('.//a/@href').get()
        if link and not link.startswith("http"):
            link = "https://www.mueller.at" + link

        # Extract headline
        headline = block.xpath('.//span[contains(@class,"headline_component_headline__headline-tag__TUdOY")]/text()').get()

        # Extract subheadline
        subheadline = block.xpath('.//span[contains(@class,"headline_component_headline__subHeadline__4nVXb")]/text()').get()

        # Write to file
        f.write(f"Category: {headline}\n")
        f.write(f"URL: {link}\n")
        f.write(f"Subheadline: {subheadline}\n")
        f.write("-" * 50 + "\n")

print(f"Saved {len(category_blocks)} categories to {output_file}")


