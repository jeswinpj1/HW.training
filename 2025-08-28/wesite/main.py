import requests
from bs4 import BeautifulSoup

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
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            return None
        
    def parse_data(self, html):
        soup = BeautifulSoup(html, "html.parser")
        links = []
        new_links1 = soup.select("div.col-sm.vertical.gap-4x > a.title.text-black.fw-500.w-fit.cap-first")
        for a in new_links1:
            full_url = a.get("href")
            links.append(full_url)
        return links   

    def parse_item(self, html):
        soup = BeautifulSoup(html, "html.parser")
        title = soup.select_one("h1.title.cap-first")
        location = soup.select_one("p.cap-first")
        data = {
            "title": title.get_text(strip=True) if title else "N/A",
            "location": location.get_text(strip=True) if location else "N/A"
        }
        return data

    def save_raw_html(self, html, filename="raw.html"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

    def save_cleaned_data(self, filename="cleaned_data.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            for item in self.results:
                f.write(f"{item['title']} | {item['location']}\n")

    def start(self):
        main_html = self.fetch_html(self.start_url)
        if not main_html:
            print("[ERROR] Could not fetch main page.")
            return
        self.save_raw_html(main_html, "raw.html")
        links = self.parse_data(main_html)
        for idx, url in enumerate(links[:20], start=1):  
            html = self.fetch_html(url)
            if html:
                data = self.parse_item(html)
                self.results.append(data)
        self.save_cleaned_data("cleaned_data.txt")

    def close(self):
        self.session.close()

if __name__ == "__main__":
    parser = QuickeralaParser()
    parser.start()
    parser.close()