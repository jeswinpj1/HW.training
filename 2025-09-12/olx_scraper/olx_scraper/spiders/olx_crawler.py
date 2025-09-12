import scrapy

API_KEY = "504eeef7c076dfcf401adae86875886d"
PROXY = f"http://scraperapi.device_type=desktop.max_cost=2.session_number=1:{API_KEY}@proxy-server.scraperapi.com:8001"

class OlxCrawlerSpider(scrapy.Spider):
    name = "olx_crawler"
    allowed_domains = ["olx.in"]

    start_urls = [
        "https://www.olx.in/en-in/kerala_g2001160/for-sale-houses-apartments_c1725"
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={"proxy": PROXY})

    def parse(self, response):
        # Extract listing links
        links = response.xpath("//a[contains(@href,'/item/')]/@href").getall()
        for link in links:
            yield {"url": response.urljoin(link)}

        # Pagination
        next_page = response.xpath("//a[contains(@rel,'next')]/@href").get()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse,
                meta={"proxy": PROXY}
            )
