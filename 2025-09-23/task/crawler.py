import time
import json
import logging
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from lxml import html
from pymongo import MongoClient
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BASE_URL = "https://www.realtysouth.com/"
REQUEST_SLEEP = 2
MAX_PAGES = 1

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "realtysouth"
COLLECTION = "agent_urls"


def get_status_code(driver, url):
    """Get HTTP status code from performance logs"""
    logs = driver.get_log("performance")
    for entry in reversed(logs):
        try:
            msg = json.loads(entry["message"])
            resp = msg["message"]
            if (
                resp["method"] == "Network.responseReceived"
                and resp["params"]["response"]["url"].startswith(url)
            ):
                return resp["params"]["response"]["status"]
        except Exception:
            continue
    return None


def get_tree(driver, url):
    driver.get(url)
    time.sleep(REQUEST_SLEEP)

    status_code = get_status_code(driver, url)
    page_source = driver.page_source

    print(f"\n--- Response from {url} ---\n")
    print("Status Code:", status_code)
    print("Length of HTML:", len(page_source))
    print(page_source[:1000])  # preview
    print("\n--------------------------\n")

    return html.fromstring(page_source)

def scroll_until_all_agents_loaded(driver, pause=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height



def find_our_agents_url(driver):
    """Find Our Agents link with XPath"""
    el = driver.find_element(By.XPATH, "//ul[@class='dropdown']//a[contains(text(),'Our Agents')]")
    return el.get_attribute("href") if el else None


def extract_agent_links(driver):
    """Extract agent profile links from page"""
    els = driver.find_elements(By.XPATH, ".//a[contains(@href,'/bio/')]")
    return [el.get_attribute("href") for el in els]


def normalize_page_url(base_url, page_num):
    parsed = urlparse(base_url)
    qs = parse_qs(parsed.query)
    qs["page"] = [str(page_num)]
    new_query = urlencode({k: v[0] for k, v in qs.items()})
    return urlunparse(parsed._replace(query=new_query))


def main():
    # Mongo
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    col = db[COLLECTION]
    col.create_index("url", unique=True)

    # undetected_chromedriver with logging enabled
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")   # comment this to see browser
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")

    # set logging directly on options
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = uc.Chrome(options=chrome_options)

    # Step 1: homepage
    get_tree(driver, BASE_URL)
    our_agents_url = find_our_agents_url(driver)
    if not our_agents_url:
        logging.error("Could not find Our Agents link")
        driver.quit()
        return
    logging.info("Our Agents page: %s", our_agents_url)

    # Step 2: crawl listing pages
    seen = set()
    for page_num in range(1, MAX_PAGES + 1):
        page_url = normalize_page_url(our_agents_url, page_num)
        logging.info("Fetching: %s", page_url)
        driver.get(page_url)
        scroll_until_all_agents_loaded(driver)


        agent_links = extract_agent_links(driver)
        if not agent_links:
            logging.info("No agent links on page %s, stopping.", page_num)
        break

# Save one document for the page
    doc = {
            "url": our_agents_url,
            "agents": agent_links
         }
    col.update_one({"url": our_agents_url}, {"$set": doc}, upsert=True)
    print(f"Saved {len(agent_links)} agents under {our_agents_url}")


    driver.quit()
    logging.info("Done. Total agent URLs collected: %d", len(seen))


if __name__ == "__main__":
    main()
