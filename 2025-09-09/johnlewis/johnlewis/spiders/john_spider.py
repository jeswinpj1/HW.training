import scrapy
from urllib.parse import urljoin

API_KEY = "7dba03e67549301a61fba61c49d5db29"

PROXY = (
    "http://scraperapi.retry_404=true.country_code=uk.device_type=desktop."
    f"max_cost=1.session_number=122:{API_KEY}@proxy-server.scraperapi.com:8001"
)

class JohnLewisSpider(scrapy.Spider):
    name = "john_spider"
    allowed_domains = ["johnlewis.com"]
    start_urls = ["https://www.johnlewis.com/"]

    base_url = "https://www.johnlewis.com/"   # define this to avoid NameError
    ids = ["some-id-1", "some-id-2"]          # placeholder, define your real IDs

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,   #changed from parse_home to parse
                meta={"proxy": PROXY, "handle_httpstatus_all": True}
            )

    def parse(self, response):
        category_links = response.xpath(
            '//li[@class="DesktopMenuItem-desktopMenuItem--75bbf"]/a/@href'
        ).getall()
   
        self.logger.info(f"Found {len(category_links)} categories")
        for link in category_links:
            category_url = urljoin(self.base_url, link)
            yield scrapy.Request(
                url=category_url,
                callback=self.parse_category,
                meta={"category_url": category_url, "proxy": PROXY},
            )
    def parse_category(self, response):
        category_url = response.meta["category_url"]

    # instead of looping over ids, grab all subcategory links directly
        sub_links = response.xpath("//span[@class='card-item-ImageCardItem_ctaBlock--ff1e1']/a/@href").getall()

        for sub_link in sub_links:
            full_sub_link = urljoin(self.base_url, sub_link)
            yield scrapy.Request(
            url=full_sub_link,
            callback=self.parse_subcategory,
            meta={"category_url": category_url, "sub_url": full_sub_link, "proxy": PROXY},
        )
       
    def parse_subcategory(self, response):
        category_url = response.meta["category_url"]
        sub_url = response.meta["sub_url"]

        product_links = response.xpath(
            '//li[@class="carousel_Carousel_item__0iZu6"]/a/@href'
        ).getall()

        full_links = [urljoin(self.base_url, link) for link in product_links]

        yield {
            "category": category_url,
            "subcategory": sub_url,
            "products": full_links,
        }

   