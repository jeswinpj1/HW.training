# import requests
# from urllib.parse import urljoin
# from parsel import Selector
# import pymongo
# from datetime import datetime

# # ---------- ScraperAPI Setup ----------
# API_KEY = "504eeef7c076dfcf401adae86875886d"
# SCRAPERAPI_URL = "http://api.scraperapi.com"

# def get_scraperapi_url(url):
#     """Wrap target URL for ScraperAPI"""
#     return f"{SCRAPERAPI_URL}?api_key={API_KEY}&country_code=uk&device_type=desktop&url={url}"

# # ---------- MongoDB Setup ----------
# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["johnlewis10"]
# collection = db["products"]

# HEADERS = {"User-Agent": "Mozilla/5.0"}

# # ---------- Scraper Functions ----------
# def get_category_links(start_url):
#     """Get category links from the John Lewis homepage"""
#     response = requests.get(get_scraperapi_url(start_url), headers=HEADERS, timeout=60)
#     print(f"Main page status: {response.status_code}")
#     selector = Selector(text=response.text)

#     # Categories usually have /cXXXX in URL
#     category_links = selector.xpath(
#             '//li[@class="DesktopMenuItem-desktopMenuItem--75bbf"]/a/@href'
#         ).getall()
   
#     return list(set([urljoin(start_url, link) for link in category_links]))

# def get_subcategory_links(category_url):
#     """Get subcategory links from a category page"""
#     response = requests.get(get_scraperapi_url(category_url), headers=HEADERS, timeout=60)
#     selector = Selector(text=response.text)

#     sub_links = selector.xpath("//span[@class='card-item-ImageCardItem_ctaBlock--ff1e1']/a/@href").getall()
#     return list(set([urljoin(category_url, link) for link in sub_links]))


# def get_product_urls(sub_url, base_url):
#     """Get product URLs from a subcategory page (PLP)"""
#     print(f"Fetching products from: {sub_url}")
#     res = requests.get(get_scraperapi_url(sub_url), headers=HEADERS, timeout=60)
#     sel = Selector(text=res.text)

#     # Product detail links typically contain `/p/`
#     links = sel.xpath(
#             '//li[@class="carousel_Carousel_item__0iZu6"]/a/@href'
#         ).getall()
#     product_urls = [urljoin(base_url, link) for link in links]

#     return list(set(product_urls))


# def scrape_johnlewis_products():
#     """Main function to scrape John Lewis"""
#     base_url = "https://www.johnlewis.com"
#     start_url = base_url

#     category_links = get_category_links(start_url)
#     all_data = {}

#     for cat_url in category_links:  # limit for demo
#         print(f"\nCategory: {cat_url}")

#         subcategory_links = get_subcategory_links(cat_url)
#         subcat_data = []

#         for sub_link in subcategory_links:  # limit for demo
#             print(f" Subcategory: {sub_link}")

#             product_urls = get_product_urls(sub_link, base_url)
#             subcat_data.append({
#                 "subcategory_url": sub_link,
#                 "product_urls": product_urls
#             })
#             print(f"  Found {len(product_urls)} products")

#         all_data[cat_url] = subcat_data

#     return all_data


# def insert_to_mongo(data):
#     """Insert scraped data into MongoDB"""
#     for category_url, subcats in data.items():
#         record = {
#             "category_url": category_url,
#             "subcategories": subcats,
#             "timestamp": datetime.utcnow()
#         }
#         collection.insert_one(record)

#     print(f"\nInserted {len(data)} category documents into MongoDB")


# # ---------- Main ----------
# if __name__ == "__main__":
#     product_data = scrape_johnlewis_products()
#     insert_to_mongo(product_data)






import time
import requests
from urllib.parse import urljoin
from parsel import Selector
import pymongo
from datetime import datetime

API_KEY = "504eeef7c076dfcf401adae86875886d"
SCRAPERAPI_URL = "https://api.scraperapi.com"  

def get_scraperapi_url(url):
    """Wrap target URL for ScraperAPI"""
    return f"{SCRAPERAPI_URL}?api_key={API_KEY}&country_code=uk&device_type=desktop&url={url}"

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["johnlewis"]
collection = db["products"]

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch(url, retries=3, backoff=5):
    """Fetch a URL via ScraperAPI with retries & backoff"""
    for attempt in range(1, retries + 1):
        try:
            res = requests.get(get_scraperapi_url(url), headers=HEADERS, timeout=90)
            res.raise_for_status()
            return res
        except requests.exceptions.RequestException as e:
            print(f" Attempt {attempt} failed for {url}: {e}")
            if attempt < retries:
                time.sleep(backoff * attempt)  
            else:
                print(f" Giving up on {url}")
                return None

def get_category_links(start_url):
    """Get category links from the John Lewis homepage"""
    response = fetch(start_url)
    if not response:
        return []
    print(f"Main page status: {response.status_code}")
    selector = Selector(text=response.text)

    category_links = selector.xpath(
        '//li[@class="DesktopMenuItem-desktopMenuItem--75bbf"]/a/@href'
    ).getall()
    return list(set([urljoin(start_url, link) for link in category_links]))

def get_subcategory_links(category_url):
    """Get subcategory links from a category page"""
    response = fetch(category_url)
    if not response:
        return []
    selector = Selector(text=response.text)

    sub_links = selector.xpath("//span[@class='card-item-ImageCardItem_ctaBlock--ff1e1']/a/@href").getall()
    return list(set([urljoin(category_url, link) for link in sub_links]))

def get_product_urls(sub_url, base_url):
    """Get product URLs from a subcategory page (PLP)"""
    print(f"Fetching products from: {sub_url}")
    res = fetch(sub_url)
    if not res:
        return []
    sel = Selector(text=res.text)

    links = sel.xpath(
        '//li[@class="carousel_Carousel_item__0iZu6"]/a/@href'
    ).getall()
    product_urls = [urljoin(base_url, link) for link in links]

    return list(set(product_urls))

def scrape_johnlewis_products():
    """Main function to scrape John Lewis"""
    base_url = "https://www.johnlewis.com"
    start_url = base_url

    category_links = get_category_links(start_url)
    all_data = {}
    for cat_url in category_links:  
        print(f"\nCategory: {cat_url}")

        subcategory_links = get_subcategory_links(cat_url)
        subcat_data = []

        for sub_link in subcategory_links:  
            print(f" Subcategory: {sub_link}")

            product_urls = get_product_urls(sub_link, base_url)
            subcat_data.append({
                "subcategory_url": sub_link,
                "product_urls": product_urls
            })
            print(f"   Found {len(product_urls)} products")

        all_data[cat_url] = subcat_data

    return all_data

def insert_to_mongo(data):
    """Insert scraped data into MongoDB"""
    for category_url, subcats in data.items():
        record = {
            "category_url": category_url,
            "subcategories": subcats,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(record)

    print(f"\n Inserted {len(data)} category documents into MongoDB")

if __name__ == "__main__":
    product_data = scrape_johnlewis_products()
    insert_to_mongo(product_data)
