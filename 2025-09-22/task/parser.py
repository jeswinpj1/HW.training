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
AGENTS_COLLECTION = "agents"
DETAILS_COLLECTION = "agent_details"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
agents_collection = db[AGENTS_COLLECTION]
details_collection = db[DETAILS_COLLECTION]


# ----------------- Parser Class -----------------
class EbbyParser:
    def __init__(self):
        self.driver = None

    def start_driver(self):
        logging.info("Starting undetected Chrome driver...")
        options = uc.ChromeOptions()
        options.headless = False
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = uc.Chrome(options=options)
        logging.info("Driver started.")

    def open_page(self, url):
        logging.info(f"Opening page: {url}")
        self.driver.get(url)
        time.sleep(5)  # wait for page load / Cloudflare
        logging.info("Page loaded.")

    def safe_xpath(self, xpath, attr=None):
        """Return element text or attribute; empty string if not found."""
        try:
            el = self.driver.find_element(By.XPATH, xpath)
            if attr:
                value = el.get_attribute(attr)
                return value.strip() if value else ""
            else:
                value = el.text
                return value.strip() if value else ""
        except:
            return ""

    def parse_agent(self, agent_url, office_url):
        """Extract agent details from profile page"""
        self.open_page(agent_url)
        # --- Extract name ---
        full_name = self.safe_xpath("//section[contains(@class,'rng-bio-account-content-office')]/h1")
        name_parts = full_name.split()
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""
        last_name = name_parts[-1] if len(name_parts) > 1 else ""

        record = {
            "profile_url": agent_url,
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "image_url": self.safe_xpath("//div[contains(@class,'rng-bio-account-slider')]/img", attr="src"),
            "office_name": self.safe_xpath("//selection[@class='rng-bio-account-content-office']/div/strong"),
            "address": self.safe_xpath("//a[contains(@class,'rng-bio-account-content-office-driving-directions')/@href"),
            "description": self.safe_xpath("//div[contains(@id,'body-text-1-preview-7321-6626912')]"),
            "languages": [lang.text.strip() for lang in self.driver.find_elements(By.XPATH, "//ul[@class='agent-languages']/li")] or [],
            "social": [el.get_attribute("href") for el in self.driver.find_elements(By.XPATH, "//ul[@class='rng-agent-bio-content-contact-social']//a")] or [""],
            "website": self.safe_xpath("//a[contains(@class,'button')]", attr="href"),
            "title": self.safe_xpath("//section[@class='rng-bio-account-content-office']/div/span"),
            "phone": self.safe_xpath("//section[@class='rng-bio-account-details']/ul/li[strong[text()='Primary']]/a"),
            "email": self.safe_xpath("//section[@class='rng-bio-account-details']/ul/li[strong[text()='Email']]/a"),
            "office_url": office_url
        }

        # Save/update in MongoDB
        details_collection.update_one(
            {"profile_url": agent_url}, {"$set": record}, upsert=True
        )
        logging.info(f"Saved agent details: {agent_url}")

    def run(self):
        self.start_driver()
        try:
            # Load all offices & agent URLs from DB
            offices = agents_collection.find({}, {"office_url": 1, "agent_urls": 1})
            for office in offices:
                office_url = office.get("office_url", "")
                agent_urls = office.get("agent_urls", [])

                for agent_url in agent_urls:
                    self.parse_agent(agent_url, office_url)

        finally:
            logging.info("Closing driver...")
            self.driver.quit()
            logging.info("Driver closed.")


# ----------------- Main -----------------
if __name__ == "__main__":
    parser = EbbyParser()
    parser.run()
