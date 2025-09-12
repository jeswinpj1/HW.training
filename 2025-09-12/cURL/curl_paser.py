# import json
# import time
# import random
# import tracemalloc
# import pycurl
# from io import BytesIO
# from lxml import html
# from pymongo import MongoClient

# # ScraperAPI credentials
# API_KEY = "7dba03e67549301a61fba61c49d5db29"
# #PROXY = f"http://scraperapi.device_type=desktop.max_cost=2.session_number=1:{API_KEY}@proxy-server.scraperapi.com:8001"
# PROXY = f"http://scraperapi.device_type=desktop.auto_headers=true.max_cost=2:{API_KEY}@proxy-server.scraperapi.com:8001"
# INPUT_FILE = "crawler_urls.json"
# OUTPUT_FILE = "olx_listings.json"
# USER_AGENTS_FILE = "/home/user/HW.training/2025-09-12/user_agents.txt"

# MAX_RETRIES = 3
# TIMEOUT = 15

# def load_user_agents(file_path):
#     with open(file_path, "r") as f:
#         return [line.strip() for line in f if line.strip()]

# def get_html_with_pycurl(url, user_agent):
#     """
#     Fetches the HTML content of a URL using PycURL with a proxy.
#     """
#     buffer = BytesIO()
#     c = pycurl.Curl()
    
#     # Set proxy options
#     c.setopt(c.PROXY, PROXY)
#     c.setopt(c.PROXYAUTH, pycurl.HTTPAUTH_ANY)
    
#     c.setopt(c.URL, url)
#     c.setopt(c.WRITEDATA, buffer)
#     c.setopt(c.FOLLOWLOCATION, 1)  # Follow redirects
#     c.setopt(c.TIMEOUT, TIMEOUT)
#     c.setopt(c.USERAGENT, user_agent)
    
#     # Force HTTP/1.1 to avoid HTTP/2 errors with proxies
#     c.setopt(c.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)

#     try:
#         c.perform()
#         response_code = c.getinfo(pycurl.RESPONSE_CODE)
#         if response_code != 200:
#             raise pycurl.error(pycurl.E_HTTP_RETURNED_ERROR, f"HTTP Error: {response_code}")
        
#         c.close()
#         html_content = buffer.getvalue().decode('utf-8')
#         return html_content

#     except pycurl.error as e:
#         print(f"[ERROR] PycURL Error: {e}")
#         return None

# def parse_olx_listings():
#     # Load user agents
#     USER_AGENTS = load_user_agents(USER_AGENTS_FILE)
#     if not USER_AGENTS:
#         print("[ERROR] No user agents found!")
#         return

#     # Connect to MongoDB
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["curl_olx_db"]
#     collection = db["data_listings"]

#     tracemalloc.start()
#     start_time = time.time()

#     # Load URLs from crawler
#     with open(INPUT_FILE) as f:
#         urls = [entry["url"] for entry in json.load(f)]

#     listings = []

#     for idx, url in enumerate(urls, start=1):
#         url_start = time.time()
#         success = False

#         for attempt in range(1, MAX_RETRIES + 1):
#             user_agent = random.choice(USER_AGENTS)
            
#             print(f"[INFO] Processing {idx}/{len(urls)}: {url} (Attempt {attempt}) with UA: {user_agent}")

#             html_content = get_html_with_pycurl(url, user_agent)

#             if html_content:
#                 try:
#                     tree = html.fromstring(html_content)

#                     # Extract fields
#                     title = tree.xpath("//h1/text()")
#                     title = title[0].strip() if title else ""

#                     price = tree.xpath("//span[contains(@class,'T8y-z')]/text()")
#                     price = price[0].strip() if price else ""

#                     location = tree.xpath("//span[contains(@class,'_1RkZP')]/text()")
#                     location = location[0].strip() if location else ""

#                     description = tree.xpath("//div[@data-aut-id='itemDescriptionContent']//text()")
#                     description = " ".join([d.strip() for d in description if d.strip()])

#                     listing = {
#                         "url": url,
#                         "title": title,
#                         "price": price,
#                         "location": location,
#                         "description": description,
#                     }

#                     listings.append(listing)

#                     # Save in MongoDB (upsert)
#                     collection.update_one(
#                         {"url": url},
#                         {"$set": listing},
#                         upsert=True
#                     )

#                     print(f"[SAVED] {title} -> MongoDB & JSON buffer")
#                     success = True
#                     break
                
#                 except Exception as e:
#                     print(f"[WARN] Parsing failed for {url}: {e}")
            
#             time.sleep(random.uniform(2, 4))

#         if not success:
#             print(f"[ERROR] Skipping {url} after {MAX_RETRIES} attempts")

#         url_end = time.time()
#         print(f"[INFO] Time taken for this URL: {url_end - url_start:.2f}s")

#     # Save all to JSON
#     with open(OUTPUT_FILE, "w") as f:
#         json.dump(listings, f, indent=2)

#     end_time = time.time()
#     current, peak = tracemalloc.get_traced_memory()
#     tracemalloc.stop()

#     print(f"[DONE] Saved {len(listings)} listings to {OUTPUT_FILE} & MongoDB")
#     print(f"[INFO] Total time: {end_time - start_time:.2f}s")
#     print(f"[INFO] Current memory usage: {current / 1024 / 1024:.2f} MB; Peak: {peak / 1024 / 1024:.2f} MB")

# if __name__ == "__main__":
#     parse_olx_listings()


import json
import time
import random
import tracemalloc
import pycurl
from io import BytesIO
from lxml import html
from pymongo import MongoClient

# ScraperAPI credentials
API_KEY = "7dba03e67549301a61fba61c49d5db29"
# The proxy string will now be dynamically created to include a session number
PROXY_BASE = f"http://scraperapi.device_type=desktop.auto_headers=true.max_cost=2"
INPUT_FILE = "crawler_urls.json"
OUTPUT_FILE = "olx_listings.json"
USER_AGENTS_FILE = "/home/user/HW.training/2025-09-12/user_agents.txt"

MAX_RETRIES = 5  # Increased the retry limit
TIMEOUT = 30     # Increased the timeout to give the proxy more time

def load_user_agents(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def get_html_with_pycurl(url, user_agent, session_num):
    """
    Fetches the HTML content of a URL using PycURL with a dynamic proxy session.
    """
    # Create a dynamic proxy string for each attempt
    proxy_url = f"{PROXY_BASE}.session_number={session_num}:{API_KEY}@proxy-server.scraperapi.com:8001"
    
    buffer = BytesIO()
    c = pycurl.Curl()
    
    # Set proxy options
    c.setopt(c.PROXY, proxy_url)
    c.setopt(c.PROXYAUTH, pycurl.HTTPAUTH_ANY)
    
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.FOLLOWLOCATION, 1)  # Follow redirects
    c.setopt(c.TIMEOUT, TIMEOUT)
    c.setopt(c.USERAGENT, user_agent)
    
    # Force HTTP/1.1 to avoid HTTP/2 errors with proxies
    c.setopt(c.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)

    try:
        c.perform()
        response_code = c.getinfo(pycurl.RESPONSE_CODE)
        if response_code != 200:
            raise pycurl.error(pycurl.E_HTTP_RETURNED_ERROR, f"HTTP Error: {response_code}")
        
        c.close()
        html_content = buffer.getvalue().decode('utf-8')
        return html_content

    except pycurl.error as e:
        print(f"[ERROR] PycURL Error: {e}")
        return None

def parse_olx_listings():
    # Load user agents
    USER_AGENTS = load_user_agents(USER_AGENTS_FILE)
    if not USER_AGENTS:
        print("[ERROR] No user agents found!")
        return

    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["curl_olx_db"]
    collection = db["data_listings"]

    tracemalloc.start()
    start_time = time.time()

    # Load URLs from crawler
    with open(INPUT_FILE) as f:
        urls = [entry["url"] for entry in json.load(f)]

    listings = []

    for idx, url in enumerate(urls, start=1):
        url_start = time.time()
        success = False

        for attempt in range(1, MAX_RETRIES + 1):
            user_agent = random.choice(USER_AGENTS)
            
            print(f"[INFO] Processing {idx}/{len(urls)}: {url} (Attempt {attempt}) with UA: {user_agent}")

            # Pass the attempt number as the session number to get a new IP
            html_content = get_html_with_pycurl(url, user_agent, attempt)

            if html_content:
                try:
                    tree = html.fromstring(html_content)

                    # Extract fields
                    title = tree.xpath("//h1/text()")
                    title = title[0].strip() if title else ""

                    price = tree.xpath("//span[contains(@class,'T8y-z')]/text()")
                    price = price[0].strip() if price else ""

                    location = tree.xpath("//span[contains(@class,'_1RkZP')]/text()")
                    location = location[0].strip() if location else ""

                    description = tree.xpath("//div[@data-aut-id='itemDescriptionContent']//text()")
                    description = " ".join([d.strip() for d in description if d.strip()])

                    listing = {
                        "url": url,
                        "title": title,
                        "price": price,
                        "location": location,
                        "description": description,
                    }

                    listings.append(listing)

                    # Save in MongoDB (upsert)
                    collection.update_one(
                        {"url": url},
                        {"$set": listing},
                        upsert=True
                    )

                    print(f"[SAVED] {title} -> MongoDB & JSON buffer")
                    success = True
                    break
                
                except Exception as e:
                    print(f"[WARN] Parsing failed for {url}: {e}")
            
            time.sleep(random.uniform(5, 10)) # Increased the random delay

        if not success:
            print(f"[ERROR] Skipping {url} after {MAX_RETRIES} attempts")

        url_end = time.time()
        print(f"[INFO] Time taken for this URL: {url_end - url_start:.2f}s")

    # Save all to JSON
    with open(OUTPUT_FILE, "w") as f:
        json.dump(listings, f, indent=2)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"[DONE] Saved {len(listings)} listings to {OUTPUT_FILE} & MongoDB")
    print(f"[INFO] Total time: {end_time - start_time:.2f}s")
    print(f"[INFO] Current memory usage: {current / 1024 / 1024:.2f} MB; Peak: {peak / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    parse_olx_listings()