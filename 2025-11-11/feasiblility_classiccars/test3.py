

import requests
from parsel import Selector
import json
import time


class ClassicCarsScraper:
    def __init__(self, input_file, output_file, limit=1000):
        self.input_file = input_file
        self.output_file = output_file
        self.limit = limit
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.classiccars.com/",
            "Connection": "keep-alive",
        }

        self.cookies = {
            "IDE": "AHWqTUkOeRTNh07YhdhUD176dl3is_181CUVbLfHUzDhrBJt7Oj6pRD_hha5KKGkPu4",
            "DSID": "AEhM4MfwkxlssRFoHWRFN-HIBBA0Wkv21MqEMJpvO5mjya5kQgqh-mwVXswfNp_mDP-PPAxaeXf2Cz6VCB9lYuu63G8n82egqk3KiKNHSUF3P50Ru_PyoJfjlqKvOrKy8MHrxOHxkDrxnMRMtGTTdgc0NwGGigl0mceTqcbl47u8FfIsyI1zCjQ9Tt_sB6JVilPfJ1xyXgJygkl7eNamD8IaJthw2YZj4l_T-0NMLJdWedMDsqcCkvrXzJY4K7rQn9Y5N1MKRjjJJkeRDCoh6m7uKLGAa4FyzzTANStQDnJ7i_1y8TbR4TY",
        }

        self.session = requests.Session()
        self.all_cars = []
        self.success = 0
        self.failure = 0
    def normalize_url(self, url: str) -> str:
            url = url.strip()
            # Remove accidental duplication like "classiccars.comhttps://"
            if "classiccars.comhttps://" in url:
                url = url.split("classiccars.comhttps://")[-1]
                url = "https://" + url
            return url
    def load_urls(self):
        with open(self.input_file, "r") as f:
            urls = json.load(f)
        return urls[: self.limit]

    def scrape_details(self, url):
        response = self.session.get(url, headers=self.headers, cookies=self.cookies)
        if response.status_code != 200:
            print(f" Failed ({response.status_code}): {url}")
            self.failure += 1
            return None

        sel = Selector(text=response.text)
    
        image_urls = [
            img if img.startswith("http") else f"https://classiccars.com{img}"
            for img in sel.xpath(
                '//div[@id="MCThumbsRapper"]//img/@src | //div[@id="MCThumbsRapper"]//img/@data-src'
            ).getall()
        ]

        description = " ".join(
            [d.strip() for d in sel.xpath('//div[contains(@class,"description")]//text()').getall() if d.strip()]
        )

        car_data = {
            "source_url": url,
            "make": sel.xpath('//li[contains(@class,"p-manufacturer")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "model": sel.xpath('//li[contains(@class,"p-model")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "year": sel.xpath('//li[contains(@class,"dt-start")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "VIN": sel.xpath('//li[contains(@class,"p-vin")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "price": sel.xpath('//li[contains(@class,"p-price")]//span[contains(@class,"red")]/text()').get(default="").strip(),
            "mileage": sel.xpath('//li[contains(@class,"p-odometer")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "transmission": sel.xpath('//li[contains(@class,"p-transmission")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "engine": sel.xpath('//li[contains(@class,"p-engine")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "exterior_color": sel.xpath('//li[contains(@class,"p-color")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "interior_color": sel.xpath('//li[contains(@class,"p-interiorColor")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "fuel_type": "",
            "body_style": "",
            "restoration_history": sel.xpath('//li[span[contains(text(),"Restoration History")]]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "exterior_condition": sel.xpath('//li[span[contains(text(),"Exterior Condition")]]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "engine_history": sel.xpath('//li[span[contains(text(),"Engine History")]]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "engine_condition": sel.xpath('//li[contains(@class,"p-condition")]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "drive_train": sel.xpath('//li[span[contains(text(),"Drive Train")]]//span[contains(@class,"gray")]/text()').get(default="").strip(),
            "description": description,
            "image_urls": image_urls,
        }

        self.success += 1
        return car_data

    def run(self):
        urls = self.load_urls()
        total_requests = len(urls)
        print(f" Processing {total_requests} listings...\n")

        for idx, url in enumerate(urls, start=1):
            clean_url = self.normalize_url(url)
            print(f"[{idx}/{total_requests}] {clean_url}")
            car_data = self.scrape_details(clean_url)
            if car_data:
                self.all_cars.append(car_data)
                if "classiccars.com" not in clean_url:
                    print(f" Skipping external link: {clean_url}")
                    self.failure += 1
                    continue

            time.sleep(0.5)

        with open(self.output_file, "w") as f:
            json.dump(self.all_cars, f, indent=4)

        # --- Summary ---
        success_rate = (self.success / total_requests) * 100 if total_requests else 0
        failure_rate = (self.failure / total_requests) * 100 if total_requests else 0

        print("\n-------- SUMMARY --------")
        print(f"Total Requests: {total_requests}")
        print(f"Success: {self.success}")
        print(f"Failure: {self.failure}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Failure Rate: {failure_rate:.2f}%")
        print("--------------------------")

        print(f"\n Done! Collected details for {self.success} cars.")
        print(f" Saved to {self.output_file}")


if __name__ == "__main__":
    scraper = ClassicCarsScraper(
        input_file="classiccars_until1990_urls.json",
        output_file="classiccars_until1990_details.json",
        limit=1000
    )
    scraper.run()
