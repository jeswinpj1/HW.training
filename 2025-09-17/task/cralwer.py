from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from pymongo import MongoClient
import time

BASE_URL = "https://2xlhome.com/ae"

# ---------------- MongoDB ---------------- #
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "scraper_db"
COLLECTION_NAME = "products"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ---------------- Selenium ---------------- #
options = Options()
options.headless = False  # change to True if you want no browser window
driver = webdriver.Chrome(options=options)
driver.get(BASE_URL)
time.sleep(5)  # wait for JS menu to render

# ---------------- Main Categories ---------------- #
main_category_elements = driver.find_elements(
    By.XPATH,
    '//ul[contains(@class,"md-top-menu-items")]/li[contains(@class,"category-item")]/a'
)

main_categories = []
for el in main_category_elements:
    url = el.get_attribute("href")
    name = el.text.strip()
    main_categories.append({"name": name, "url": url})

print("Top-level categories:")
for cat in main_categories:
    print("-", cat["name"], cat["url"])

# ---------------- Subcategories ---------------- #
for cat in main_categories:
    driver.get(cat["url"])
    time.sleep(3)
    subcat_elements = driver.find_elements(
        By.XPATH,
        '//a[contains(@class,"subcategories-product-link")]'
    )
    subcategories = []
    for sub in subcat_elements:
        sub_url = sub.get_attribute("href")
        sub_name = sub.text.strip()
        subcategories.append({"name": sub_name, "url": sub_url})
    cat["subcategories"] = subcategories

# ---------------- Products ---------------- #
for cat in main_categories:
    for sub in cat.get("subcategories", []):
        driver.get(sub["url"])
        time.sleep(2)
        product_elements = driver.find_elements(
            By.XPATH,
            '//a[contains(@class,"product-item-link")]'
        )
        products = []
        for p in product_elements:
            prod_url = p.get_attribute("href")
            products.append(prod_url)
        sub["products"] = products

# ---------------- Save to MongoDB ---------------- #
collection.insert_many(main_categories)
print("Scraping complete. Data saved to MongoDB.")

driver.quit()
