
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

    def clean_field(self, value, join=False):
      
        if not value:
            return ""

        if isinstance(value, list):
            cleaned = [v.strip() for v in value if v and v.strip()]
            if join:
                return " ".join(cleaned) if cleaned else ""
            return ", ".join(cleaned) if cleaned else ""

        if isinstance(value, str):
            return value.strip()

        return ""

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
        category = self.clean_field(response.meta.get("category", ""))
        subcategory = self.clean_field(response.meta.get("subcategory", ""))

        title = self.clean_field(
            response.xpath("//span[@data-testid='product:title:content']/text()").get()
        )
        price = self.clean_field(
            response.xpath("//span[@class='price_price__now__bNSvu']/text()").get()
        )
        description = self.clean_field(
            response.xpath("//div[@class='ProductDescriptionAccordion_descriptionContent__yd_yu']/p/text()").getall(),
            join=True
        )
        unique_id = response.xpath("//p[@data-testid='description:code']/strong/text()").getall()
            
        brand = self.clean_field(
            response.xpath("//span[contains(@data-testid,'product:title')]/text()").get()
        )
        color = self.clean_field(
            response.xpath("//h3[@data-testid='colourlist:label']/span/text()").getall()
        )

        yield {
            "category": category,
            "subcategory": subcategory,
            "url": response.url or "",
            "title": title,
            "price": price,
            "description": description,
            "unique_id": unique_id,
            "brand": brand,
            "color": color,
        }
