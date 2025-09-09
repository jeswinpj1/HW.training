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
        # Load the category-subcategory-products structure
        with open("output.json", "r") as f:
            data = json.load(f)

        for entry in data:
            category = entry.get("category")
            subcategory = entry.get("subcategory")
            products = entry.get("products", [])
            print(f"Category: {category}, Subcategory: {subcategory}, Products: {len(products)}")
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
        category = response.meta["category"]
        subcategory = response.meta["subcategory"]

        # Adjust selectors depending on John Lewis product page structure
        title = response.xpath("//span[@data-testid='product:title:content']/text()").get()
        price = response.xpath("//span[@class='price_price__now__bNSvu']/text()").get()
        description = response.xpath("//div[@class='ProductDescriptionAccordion_descriptionContent__yd_yu']/p/text()").getall()
        uniqe_id=response.xpath("//p[@data-testid='description:code']/strong/text()").get()
        brand=response.xpath("//span[@data-testid='product:title:johnlewis']/text()").get()
        color=response.xpath("//h3[@class='colour_c-colourList__title__SSuM1']/span/text()").get()
        # Clean description
        description = " ".join([d.strip() for d in description if d.strip()])

        yield {
            "category": category,
            "subcategory": subcategory,
            "url": response.url,
            "title": title,
            "price": price,
            "description": description,
            "unique_id":uniqe_id,
            "brand":brand,
            "color":color if color else None,
        }
