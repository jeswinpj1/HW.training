import scrapy
import json
from urllib.parse import urljoin

API_KEY = "7dba03e67549301a61fba61c49d5db29"

PROXY = (
    "http://scraperapi.retry_404=true.country_code=uk.device_type=desktop."
    f"max_cost=1.session_number=222:{API_KEY}@proxy-server.scraperapi.com:8001"
)

class JohnLewisProductSpider(scrapy.Spider):
    name = "john_products"
    allowed_domains = ["johnlewis.com"]

    def start_requests(self):
        with open("output.json", "r") as f:
            data = json.load(f)

        for entry in data:
            category = entry.get("category", "")
            subcategory = entry.get("subcategory", "")
            products = entry.get("products", [])
            for product_url in products:
                yield scrapy.Request(
                    url=product_url,
                    callback=self.parse_product,
                    meta={
                        "proxy": PROXY,
                        "category": category,
                        "subcategory": subcategory,
                    }
                )
           
    def parse_product(self, response):
        category = response.meta.get("category", "")
        subcategory = response.meta.get("subcategory", "")
        title = response.xpath("//span[@data-testid='product:title:content']/text()").get(default="")
        price = response.xpath("//span[@class='price_price__now__bNSvu']/text()").get(default="")
        description = response.xpath("//div[@class='ProductDescriptionAccordion_descriptionContent__yd_yu']/p/text()").getall()
        unique_id = response.xpath("//p[@data-testid='description:code']/strong/text()").getall()
        brand = response.xpath("//span[contains(@data-testid,'product:title')]/text()").get(default="")
        color = response.xpath("//h3[@data-testid='colourlist:label']/span/text()").getall()
        description = " ".join([d.strip() for d in description if d.strip()])

        yield {
            "category": category or "",
            "subcategory": subcategory or "",
            "url": response.url or "",
            "title": title or "",
            "price": price or "",
            "description": description or "",
            "unique_id": unique_id or "",
            "brand": brand or "",
            "color": color if color else "",
        }
