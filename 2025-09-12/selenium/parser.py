import json
import time
import random
import tracemalloc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient

INPUT_FILE = "crawler_urls.json"
OUTPUT_FILE = "olx_listings.json"
USER_AGENTS_FILE = "/home/user/HW.training/2025-09-12/user_agents.txt"

MAX_RETRIES = 3  # number of retries per URL

def load_user_agents(file_path):
    with open(file_path, "r") as f:
        agents = [line.strip() for line in f if line.strip()]
    return agents

def parse_olx_listings():
    # Load user agents
    USER_AGENTS = load_user_agents(USER_AGENTS_FILE)
    if not USER_AGENTS:
        print("[ERROR] No user agents found!")
        return

    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")  # update if remote DB
    db = client["selenium_olx1_db"]
    collection = db["data_listings"]

    # Start measuring memory
    tracemalloc.start()
    start_time = time.time()

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    # Load URLs from crawler
    with open(INPUT_FILE) as f:
        urls = [entry["url"] for entry in json.load(f)]

    listings = []

    for idx, url in enumerate(urls, start=1):
        url_start = time.time()
        success = False

        for attempt in range(1, MAX_RETRIES + 1):
            user_agent = random.choice(USER_AGENTS)
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
            print(f"[INFO] Processing {idx}/{len(urls)}: {url} (Attempt {attempt}) with UA: {user_agent}")

            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h1"))
                )

                title = driver.find_element(By.XPATH, "//h1").text.strip()

                price_elem = driver.find_elements(By.XPATH, "//span[contains(@class,'T8y-z')]")
                price = price_elem[0].text.strip() if price_elem else ""

                location_elem = driver.find_elements(By.XPATH, "//span[contains(@class,'_1RkZP')]")
                location = location_elem[0].text.strip() if location_elem else ""

                description_elem = driver.find_elements(By.XPATH, "//div[@data-aut-id='itemDescriptionContent']")
                description = description_elem[0].text.strip() if description_elem else ""

                listing = {
                    "url": url,
                    "title": title,
                    "price": price,
                    "location": location,
                    "description": description
                }

                listings.append(listing)

                # Insert into MongoDB
                collection.update_one(
                    {"url": url},  # prevent duplicates
                    {"$set": listing},
                    upsert=True
                )

                print(f"[SAVED] {title} -> MongoDB & JSON buffer")
                success = True
                break
            except Exception as e:
                print(f"[WARN] Attempt {attempt} failed for {url}: {e}")
                time.sleep(random.uniform(2, 4))

        if not success:
            print(f"[ERROR] Skipping {url} after {MAX_RETRIES} attempts")

        url_end = time.time()
        print(f"[INFO] Time taken for this URL: {url_end - url_start:.2f}s")

    driver.quit()

    # Save all listings to JSON
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
