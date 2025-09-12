import scrapy
import json
from ..items import OlxItem  # make sure OlxItem is defined in items.py

API_KEY = "504eeef7c076dfcf401adae86875886d"
PROXY = f"http://scraperapi.device_type=desktop.max_cost=2.session_number=1:{API_KEY}@proxy-server.scraperapi.com:8001"

class OlxParserSpider(scrapy.Spider):
    name = "olx_parser"
    allowed_domains = ["olx.in"]

    def start_requests(self):
        # Read crawler output file
        with open("listing_urls.json") as f:
            data = json.load(f)
            for entry in data:
                url = entry["url"]
                yield scrapy.Request(url, callback=self.parse_item, meta={"proxy": PROXY})

    def parse_item(self, response):
        item = OlxItem()
        item["details"] = response.xpath("//h1/text()").get(default="").strip()
        item["price"] = response.xpath("//span[contains(@class,'T8y-z')]/text()").re_first(r"[\d,]+")
        item["location"] = response.xpath("//span[contains(@class,'_1RkZP')]/text()").get(default="").strip()
        item["description"] =" ".join(response.xpath("//div[@data-aut-id='itemDescriptionContent']//text()").getall()).strip()
        item["url"] = response.url
        yield item

