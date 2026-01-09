# import requests
# from parsel import Selector

# url = "https://www.walmart.com"
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
# }

# response = requests.get(url, headers=headers)
# print("Status Code:", response.status_code)

# sel = Selector(text=response.text)

# # Use contains() to match class partially (safer for dynamic classes)
# urls = sel.xpath('//a[contains(@class,"flex items-center b--none bg-transparent mr3 pa0 pointer h3 w3 no-underline white")]/@href').getall()

# # Convert relative URLs to absolute
# absolute_urls = []
# for link in urls:
#     if link.startswith("http"):
#         absolute_urls.append(link)
#     else:
#         absolute_urls.append(f"https://www.walmart.com{link}")

# print(f"Total links found: {len(absolute_urls)}")
# for l in absolute_urls[:20]:  # print first 20 links
#     print(l)


#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ main category urls code ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#



import requests
from parsel import Selector

BASE_URL = "https://www.walmart.com"
ALL_DEPT_URL = f"{BASE_URL}/all-departments"

headers = {
    "authority": "www.walmart.com",
    "method": "GET",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br, zstd",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
}

# Step 1: Request the all-departments page
response = requests.get(ALL_DEPT_URL, headers=headers)
print("All Departments Page Status:", response.status_code)

sel = Selector(text=response.text)

# Step 2: Extract subcategory links
sub_links = sel.xpath('//a[contains(@class,"f6 no-underline mid-gray db pv2 underline-hover")]/@href').getall()
sub_links = [link if link.startswith("http") else BASE_URL + link for link in sub_links]
print(f"Total subcategory links found: {len(sub_links)}")

# Step 3: Filter by keywords
keywords = ["candy", "snacks", "toys", "video-games", "videogames", "video games"]
filtered_links = [link for link in sub_links if any(kw.lower() in link.lower() for kw in keywords)]
print(f"Filtered links: {len(filtered_links)}")

# Step 4: Save to text file
with open("walmart_filtered_subcategories.txt", "w") as f:
    for link in filtered_links:
        f.write(link + "\n")

print("Filtered subcategory links saved to walmart_filtered_subcategories.txt")
