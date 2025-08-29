import requests
from bs4 import BeautifulSoup
import logging
from settings import (
    BASE_URL, START_URL, USER_AGENT, RAW_HTML_FILE, LINKS_FILE, CLEANED_DATA_FILE,
    DataMiningError, setup_logging
)

class QuickeralaParser:
    def __init__(self):
        self.base_url = BASE_URL
        self.start_url = START_URL
        self.session = requests.Session()
        self.results = []

    def fetch_html(self, url):
        try:
            logging.info(f"Fetching: {url}")
            response = self.session.get(url, headers={"User-Agent": USER_AGENT})
            response.raise_for_status()
            logging.info(f"Got response from {url}")
            return response.text
        except requests.ConnectionError as e:
            logging.error(f"Connection error while fetching {url}: {e}")
            return None
        except requests.HTTPError as e:
            logging.error(f"HTTP error while fetching {url}: {e}")
            return None
        except requests.RequestException as e:
            logging.error(f"Request exception while fetching {url}: {e}")
            return None

    def parse_data(self, html):
        try:
            soup = BeautifulSoup(html, "html.parser")
            links = []
            new_links1 = soup.select("div.col-sm.vertical.gap-4x > a.title.text-black.fw-500.w-fit.cap-first")
            if not new_links1:
                raise DataMiningError("No links found during parsing.")
            for a in new_links1:
                full_url = a.get("href")
                links.append(full_url)
            logging.info(f"Extracted {len(links)} links")
            return links
        except Exception as e:
            raise DataMiningError(f"Failed to parse data: {e}")

    def parse_item(self, html):
        try:
            soup = BeautifulSoup(html, "html.parser")
            title = soup.select_one("h1.title.cap-first")
            location = soup.select_one("p.cap-first")
            if not title or not location:
                raise DataMiningError("Missing title or location during parsing.")
            data = {
                "title": title.get_text(strip=True),
                "location": location.get_text(strip=True)
            }
            logging.info(f"Title: {data['title']} | Location: {data['location']}")
            return data
        except Exception as e:
            raise DataMiningError(f"Failed to parse item: {e}")

    def save_links_to_file(self, links, filename=LINKS_FILE):
        with open(filename, "w", encoding="utf-8") as f:
            for link in links:
                f.write(f"{link}\n")
        logging.info(f"Saved links to {filename}")

    def yield_lines_from_file(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                yield line.rstrip('\n')

    def save_raw_html(self, html, filename=RAW_HTML_FILE):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        logging.info(f"Saved raw HTML to {filename}")

    def save_cleaned_data(self, filename=CLEANED_DATA_FILE):
        with open(filename, "w", encoding="utf-8") as f:
            for item in self.results:
                f.write(f"{item['title']} | {item['location']}\n")
        logging.info(f"Saved cleaned data to {filename}")

    def start(self):
        try:
            main_html = self.fetch_html(self.start_url)
            if not main_html:
                logging.error(f"Could not fetch main page: {self.start_url}")
                return
            self.save_raw_html(main_html)
            links = self.parse_data(main_html)
            self.save_links_to_file(links)
            for url in self.yield_lines_from_file(LINKS_FILE):
                try:
                    html = self.fetch_html(url)
                    if html:
                        data = self.parse_item(html)
                        self.results.append(data)
                except DataMiningError as e:
                    logging.error(f"{e}")
                    continue
            self.save_cleaned_data()
        except DataMiningError as e:
            logging.error(f"{e}")

    def close(self):
        self.session.close()

if __name__ == "__main__":
    setup_logging()
    parser = QuickeralaParser()
    parser.start()
    parser.close()