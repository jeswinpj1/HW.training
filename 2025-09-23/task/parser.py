# import time
# import logging
# from lxml import html
# import undetected_chromedriver as uc
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from pymongo import MongoClient

# logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# MONGO_URI = "mongodb://localhost:27017/"
# DB_NAME = "realtysouth"
# URL_COLLECTION = "agent_urls"   # collection with your agent URLs
# DATA_COLLECTION = "agent_data"  # collection to save scraped agent details

# REQUEST_SLEEP = 2


# def split_name(full_name):
#     parts = full_name.strip().split()
#     first_name = parts[0] if len(parts) > 0 else ""
#     middle_name = " ".join(parts[1:-1]) if len(parts) > 2 else ""
#     last_name = parts[-1] if len(parts) > 1 else ""
#     return first_name, middle_name, last_name


# def safe_xpath(tree, xpath_expr):
#     try:
#         result = tree.xpath(xpath_expr)
#         if result:
#             if isinstance(result, list):
#                 # join if multiple text nodes
#                 return " ".join([r.strip() for r in result if r.strip()])
#             return result.strip()
#         return ""
#     except Exception:
#         return ""


# def extract_agent_details(driver, url):
#     driver.get(url)
#     time.sleep(REQUEST_SLEEP)
#     tree = html.fromstring(driver.page_source)

#     # Name and title
#     full_name = safe_xpath(tree, "//p[contains(@class,'rng-agent-profile-contact-name')]/text()")
#     first_name, middle_name, last_name = split_name(full_name)
#     title = safe_xpath(tree, "//span[contains(@class,'rng-agent-profile-contact-title')]/text()")

#     # Image
#     image_url = safe_xpath(tree, "//img[contains(@class,'rng-agent-profile-photo')]/@src")

#     # Description (if available)
#     description = safe_xpath(tree, " //div[starts-with(@id,'body-text-')]/p/text()")

#     # Contact info
#     # Extract office and agent phone numbers separately
#     office_phone_numbers = safe_xpath(tree,"//li/a[i[contains(@class,'fa-building')]]/@href")
#     office_phone_numbers = [p.replace("tel:", "").strip() for p in office_phone_numbers]

#     agent_phone_numbers = safe_xpath(tree,"//li/a[i[contains(@class,'fa-user')]]/@href")
#     agent_phone_numbers = [p.replace("tel:", "").strip() for p in agent_phone_numbers]

    
#     # Website / email
#     website = safe_xpath(tree, "//a[contains(text(),'Website')]/@href")
#     email = safe_xpath(tree, "//a[contains(@href,'mailto:')]/@href").replace("mailto:", "")

#     # Office info
   
#     address = safe_xpath(tree, "//p[contains(@class,'__web-inspector-hide-shortcut__')]/text()")
    

#     return {
#         "profile_url": url,
#         "first_name": first_name,
#         "middle_name": middle_name,
#         "last_name": last_name,
#         "title": title,
#         "image_url": image_url,
#         "description": description,
#         "website": website,
#         "email": email,
#         "address": address,
#         "country": "US",
#         "agent_phone_numbers": agent_phone_numbers,
#         "office_phone_numbers": office_phone_numbers
#     }


# def main():
#     # MongoDB setup
#     client = MongoClient(MONGO_URI)
#     db = client[DB_NAME]
#     url_col = db[URL_COLLECTION]
#     data_col = db[DATA_COLLECTION]

#     # Selenium setup
#     chrome_options = Options()
#     chrome_options.add_argument("--start-maximized")
#     chrome_options.add_argument("--disable-gpu")
#     driver = uc.Chrome(options=chrome_options)

#     # Get all agent URLs from MongoDB
#     agent_docs = url_col.find()
#     total_agents = sum(len(doc.get("agents", [])) for doc in agent_docs)
#     logging.info("Total agents to process: %d", total_agents)

#     for doc in url_col.find():
#         for agent_url in doc.get("agents", []):
#             try:
#                 logging.info("Processing: %s", agent_url)
#                 data = extract_agent_details(driver, agent_url)
#                 data_col.update_one({"profile_url": agent_url}, {"$set": data}, upsert=True)
#                 logging.info("Saved agent: %s %s", data["first_name"], data["last_name"])
#             except Exception as e:
#                 logging.error("Failed to process %s: %s", agent_url, e)

#     driver.quit()
#     logging.info("All done!")


# if __name__ == "__main__":
#     main()

#.....................................................................................................................................................................
#
#try 2


import time
import logging
from lxml import html
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ------------------ CONFIG ------------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "realtysouth"
URL_COLLECTION = "agent_urls"   # collection with agent URLs
DATA_COLLECTION = "agent_data"  # collection to save scraped agent details
REQUEST_SLEEP = 2


# ------------------ UTILITIES ------------------
def split_name(full_name):
    parts = full_name.strip().split()
    first_name = parts[0] if len(parts) > 0 else ""
    middle_name = " ".join(parts[1:-1]) if len(parts) > 2 else ""
    last_name = parts[-1] if len(parts) > 1 else ""
    return first_name, middle_name, last_name


def safe_xpath(tree, xpath_expr):
    try:
        result = tree.xpath(xpath_expr)
        if result:
            if isinstance(result, list):
                return " ".join([r.strip() for r in result if r.strip()])
            return result.strip()
        return ""
    except Exception:
        return ""


# ------------------ EXTRACT DETAILS ------------------
def extract_agent_details(driver, url):
    driver.get(url)
    time.sleep(REQUEST_SLEEP)
    tree = html.fromstring(driver.page_source)

    # Name and title
    full_name = safe_xpath(tree, "//p[contains(@class,'rng-agent-profile-contact-name')]/text()")
    first_name, middle_name, last_name = split_name(full_name)
    title = safe_xpath(tree, "//span[contains(@class,'rng-agent-profile-contact-title')]/text()")

    # Image
    image_url = safe_xpath(tree, "//img[contains(@class,'rng-agent-profile-photo')]/@src")

    # Description
    description = tree.xpath("//div[contains(@id,'body-text-1-preview-')]//text()")
    description = description[0].strip() if description else ""

# Phone numbers
    phone_numbers = tree.xpath("//ul[contains(@class,'rng-agent-profile-contact')]/li/a[starts-with(@href,'tel:')]/@href")
    phone_numbers = [p.replace("tel:", "").strip() for p in phone_numbers]

# Website
    website = tree.xpath("//li[contains(@class,'rng-agent-profile-contact-website')]/a/@href")
    website = website[0].strip() if website else ""

# Email
    email = tree.xpath("//li[contains(@class,'rng-agent-profile-contact-email')]/a/@href")
    email = email[0].strip() if email else ""
    if email.startswith("/"):
        email = "https://www.realtysouth.com" + email

# Address
    address = tree.xpath("//li[contains(@class,'rng-agent-profile-contact-address')]//text()")
    address = " ".join([a.strip() for a in address if a.strip()])

# Social media links
    social_links = tree.xpath("//li[contains(@class,'rng-agent-profile-contact-social')]//a/@href")
    social_platforms = {}
    for link in social_links:
        if "instagram.com" in link:
            social_platforms['instagram'] = link
        elif "facebook.com" in link:
            social_platforms['facebook'] = link
        elif "linkedin.com" in link:
            social_platforms['linkedin'] = link


    # Country (static)
    country = "US"

    return {
        "profile_url": url,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "title": title,
        "image_url": image_url,
        "description": description,
        "website": website,
        "email": email,
        "address": address,
        "country": country,
        "agent_phone_numbers": phone_numbers,
        "social_links": social_platforms,

    }


# ------------------ MAIN ------------------
def main():
    # MongoDB setup
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    url_col = db[URL_COLLECTION]
    data_col = db[DATA_COLLECTION]

    # Selenium setup
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    driver = uc.Chrome(options=chrome_options)

    # Load all agent docs and materialize cursor
    agent_docs = list(url_col.find())
    total_agents = sum(len(doc.get("agents", [])) for doc in agent_docs)
    logging.info("Total agents to process: %d", total_agents)

    for doc in agent_docs:
        agents_list = doc.get("agents", [])
        if not agents_list:
            logging.warning("No agents found in document %s", doc.get("url", "N/A"))
            continue

        for agent_url in agents_list:
            try:
                logging.info("Processing: %s", agent_url)
                data = extract_agent_details(driver, agent_url)
                data_col.update_one({"profile_url": agent_url}, {"$set": data}, upsert=True)
                logging.info("Saved agent: %s %s", data["first_name"], data["last_name"])
            except Exception as e:
                logging.error("Failed to process %s: %s", agent_url, e)

    driver.quit()
    logging.info("All done!")


if __name__ == "__main__":
    main()
