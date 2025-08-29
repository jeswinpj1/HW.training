import requests
from bs4 import BeautifulSoup

class DataMiningError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        if self.code is not None:
            return f"[Error code {self.code}] {self.message}"
        return self.message

class QuickeralaParser:
    def __init__(self):
        self.base_url = "https://www.quickerala.com"
        self.start_url = "https://www.quickerala.com/thrissur/real-estate/real-estate-agents/sbct-5996-dt-13"
        self.session = requests.Session()
        self.results = []

    def fetch_html(self, url):
        try:
            response = self.session.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            return response.text
        except requests.ConnectionError as e:
            print(f"Connection error while fetching {url}: {e}")
            return None
        except requests.HTTPError as e:
            print(f"HTTP error while fetching {url}: {e}")
            return None
        except requests.RequestException as e:
            print(f"Request exception while fetching {url}: {e}")
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
            return data
        except Exception as e:
            raise DataMiningError(f"Failed to parse item: {e}")

    def save_links_to_file(self, links, filename="links.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            for link in links:
                f.write(f"{link}\n")

    def yield_lines_from_file(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                yield line.rstrip('\n')

    def save_raw_html(self, html, filename="raw.html"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

    def save_cleaned_data(self, filename="cleaned_data.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            for item in self.results:
                f.write(f"{item['title']} | {item['location']}\n")

    def start(self):
        try:
            main_html = self.fetch_html(self.start_url)
            if not main_html:
                return
            self.save_raw_html(main_html, "raw.html")
            links = self.parse_data(main_html)
            self.save_links_to_file(links, "links.txt")
            for url in self.yield_lines_from_file("links.txt"):
                try:
                    html = self.fetch_html(url)
                    if html:
                        data = self.parse_item(html)
                        self.results.append(data)
                except DataMiningError as e:
                    continue
            self.save_cleaned_data("cleaned_data.txt")
        except DataMiningError as e:
            pass
    def close(self):
        self.session.close()
if __name__ == "__main__":
    parser = QuickeralaParser()
    parser.start()
    parser.close()