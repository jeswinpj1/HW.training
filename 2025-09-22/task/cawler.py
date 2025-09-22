import json
import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from pymongo import MongoClient

# ----------------- Logging Setup -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ----------------- MongoDB Setup -----------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "ebby"
COLLECTION_NAME = "agents"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


# ----------------- Scraper Class -----------------
class EbbyScraper:
    def __init__(self, url):
        self.url = url
        self.driver = None

    def start_driver(self):
        logging.info("Starting undetected Chrome driver...")
        options = uc.ChromeOptions()
        options.headless = False  # browser visible
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = uc.Chrome(options=options)
        logging.info("Driver started.")

    def open_page(self, url):
        logging.info(f"Opening page: {url}")
        self.driver.get(url)
        time.sleep(5)  # wait for Cloudflare / initial load
        logging.info("Page loaded.")

    def scroll_to_load(self, pause_time=2):
        logging.info("Scrolling to load all content...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logging.info("Reached bottom of page.")
                break
            last_height = new_height
            logging.info("New content loaded, scrolling more...")

    def get_office_urls(self):
        logging.info("Extracting office URLs...")
        office_elements = self.driver.find_elements(By.XPATH, "//article[@class='rng-agent-roster-agent-card js-sort-item']/a")
        office_urls = [el.get_attribute("href") for el in office_elements if el.get_attribute("href")]
        logging.info(f"Found {len(office_urls)} offices")
        return office_urls

    def extract_agents(self, office_url):
        logging.info(f"Opening office page: {office_url}")
        self.open_page(office_url)
        self.scroll_to_load()

        logging.info("Extracting agent URLs...")
        agent_elements = self.driver.find_elements(
            By.XPATH,
            "//a[contains(@class,'btn btn-outline-primary button hollow')]"
        )
        agent_urls = [el.get_attribute("href") for el in agent_elements if el.get_attribute("href")]
        logging.info(f"Found {len(agent_urls)} agents")

    # Save as one document: { "office_url": ..., "agent_urls": [...] }
        record = {"office_url": office_url, "agent_urls": agent_urls}
        collection.update_one(
            {"office_url": office_url}, {"$set": record}, upsert=True
        )
        logging.info(f"Saved {len(agent_urls)} agents for office: {office_url}")


    def close_driver(self):
        logging.info("Closing driver...")
        self.driver.quit()
        logging.info("Driver closed.")

    def run(self):
        self.start_driver()
        try:
            self.open_page(self.url)
            office_urls = self.get_office_urls()

            for office_url in office_urls:
                self.extract_agents(office_url)

        finally:
            self.close_driver()


# ----------------- Main -----------------
if __name__ == "__main__":
    url = "https://www.ebby.com/roster/offices"
    scraper = EbbyScraper(url)
    scraper.run()

       
            










