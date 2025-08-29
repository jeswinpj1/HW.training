import requests
from bs4 import BeautifulSoup

class QuickeralaParser:
    def __init__(self):
        self.base_url = "https://www.quickerala.com"
        self.start_url = "https://www.quickerala.com/thrissur/real-estate/real-estate-agents/sbct-5996-dt-13"
        self.session = requests.Session()
        self.results = []

    def fetch_html(self, url):
        """Fetch HTML content using requests"""
        try:
            print(f"[INFO] Fetching: {url}")
            response = self.session.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            print(f"[SUCCESS] Got response from {url}")
            return response.text
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            return None

    def parse_data(self, html):
        """Extract listing URLs from the main page"""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        kak= soup.select("div.col-sm.vertical.gap-4x > a.title.text-black.fw-500.w-fit.cap-first")
        #print(kak)
        #print(soup.prettify())
        for a in kak:  # for now, grab all <a> tags
            full_url = a.get("href")
            links.append(full_url)
        print(f"[INFO] Extracted {len(links)} links")
        return links
        
    def parse_item(self, html):
        """Extract sample details from a listing page"""
        soup = BeautifulSoup(html, "html.parser")
        title = soup.select_one("h1.title.cap-first")  # adjust later based on site structure
        location = soup.select_one("p.cap-first")  # placeholder selector

        data = {
            "title": title.get_text(strip=True) if title else "N/A",
            "location": location.get_text(strip=True) if location else "N/A"
        }
        print(f"[DATA] Title: {data['title']} | Location: {data['location']}")
        return data

    def save_to_file(self, filename="quickerala_results.txt"):
        """Save extracted results to a text file"""
        with open(filename, "w", encoding="utf-8") as f:
            for item in self.results:
                f.write(f"{item['title']} | {item['location']}\n")
        print(f"[INFO] Data saved to {filename}")

    def start(self):
        """Main entry point for crawling"""
        
        main_html = self.fetch_html(self.start_url)
        if not main_html:
            print("[ERROR] Could not fetch main page.")
            return

        links = self.parse_data(main_html)
        print(f"[INFO] Found {len(links)} links on main page")

        for idx, url in enumerate(links[:10], start=1):  # demo: limit to 10
            print(f"[INFO] Parsing page {idx}: {url}")
            html = self.fetch_html(url)
            if html:
                data = self.parse_item(html)
                self.results.append(data)

        self.save_to_file()

    def close(self):
        """Close the session"""
        self.session.close()

if __name__ == "__main__":
    parser = QuickeralaParser()
    parser.start()
    parser.close()
