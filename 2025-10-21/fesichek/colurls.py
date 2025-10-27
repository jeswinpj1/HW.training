import requests
import re
from parsel import Selector

# Step 1: URL to scrape
url = "https://www.lidl.co.uk"

# Output files
output_links_file = "navigation_links.txt"
output_ids_file = "navigation_ids.txt"
output_api_file = "navigation_api_urls.txt"

# Step 2: Send GET request to webpage
response = requests.get(url)
response.raise_for_status()

# Step 3: Parse HTML content
selector = Selector(response.text)

# Step 4: Extract all hrefs with your target class
links = selector.xpath('//a[contains(@class, "ACategoryOverviewSlider__Link")]/@href').getall()

# Step 5: Save all collected links
with open(output_links_file, "w", encoding="utf-8") as f:
    for link in links:
        f.write(link.strip() + "\n")

# Step 6 & 7: Extract numeric IDs and generate API URLs
api_base = (
    "https://www.lidl.co.uk/q/api/search?"
    "offset=12&fetchsize=12&locale=en_GB&assortment=GB&version=2.1.0&category.id="
)

with open(output_ids_file, "w", encoding="utf-8") as f_ids, open(output_api_file, "w", encoding="utf-8") as f_api:

    
    for link in links:
        match = re.search(r's(\d+)', link)  # Extract digits after 's'
        if match:
            category_id = match.group(1)
            f_ids.write(category_id + "\n")
            
            # Generate API URL
            api_url = api_base + category_id
            f_api.write(api_url + "\n")

print(f"Extracted {len(links)} links and saved to {output_links_file}")
print(f"Extracted category IDs and saved to {output_ids_file}")
print(f"Generated category API URLs and saved to {output_api_file}")
