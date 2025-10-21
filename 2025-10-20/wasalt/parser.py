
# import logging, time, requests
# from lxml import html
# from pymongo import MongoClient
# from settings import MONGO_URI, DB_NAME, SOURCE_COLLECTION, TARGET_COLLECTION, HEADERS
# from items import PropertyDetails

# class WasaltPropertyScraper:
#     def __init__(self):
#         self.client = MongoClient(MONGO_URI)
#         self.source = self.client[DB_NAME][SOURCE_COLLECTION]
#         self.target = self.client[DB_NAME][TARGET_COLLECTION]

#     def fetch(self, url):
#         logging.info(f"Fetching details: {url}")
#         r = requests.get(url, headers=HEADERS, timeout=30)
#         r.raise_for_status()
#         return r.text

#     def parse_property(self, html_content, url):
#         """Extract property details with XPath"""
#         tree = html.fromstring(html_content)

#         title = tree.xpath("string(//div[contains(@class,'stylenewPDP_pdpTitle__')])").strip()
#         price = tree.xpath("string(//div[contains(@class,'style_price__')])").strip()
#         tags = tree.xpath("//div[contains(@class,'style_pdpTagWrapper__')]/div/text()")
#         sale_status = tags[0].strip() if len(tags) > 0 else ""
#         furnished_status = tags[1].strip() if len(tags) > 1 else ""
#         location = " ".join([l.strip() for l in tree.xpath("//div[contains(@class,'stylenewPDP_propInfoAdd__')]//text()")])
#         breadcrumbs = " > ".join([b.strip() for b in tree.xpath('//div[contains(@class,"stylenewPDP_breadcrumbsWrapper__")]//li//text()')])
#         description = " ".join([p.strip() for p in tree.xpath('//div[contains(@class,"style_pdpDescWrapper__")]//p/text()') if p.strip()])

#         fal_license = tree.xpath("string(//div[contains(@class,'style_falLicense__')]//div[contains(@class,'style_value__')])").strip()
#         ref_no_text = tree.xpath("string(//div[contains(@class,'style_refferenceNumberText__')]/span[1])").strip()
#         ref_no = ref_no_text.split()[-1] if ref_no_text else ""
#         broker_name = tree.xpath("string(//p[contains(@class,'style_brokerListedName__')])").strip()

#         area_price_number = tree.xpath("string(//div[contains(@class,'style_areaDefine__')]/text())").strip()
#         area_price_unit = tree.xpath("string(//div[contains(@class,'style_areaDefine__')]/span/text())").strip()
#         price_per_sqm = f"{area_price_number} {area_price_unit}".strip() if area_price_number else ""

#         labels = tree.xpath("//div[contains(@class,'style_infoSectionInnerContainer__')]//span[contains(@class,'style_infoLable__')]/text()")
#         values = tree.xpath("//div[contains(@class,'style_infoSectionInnerContainer__')]//span[contains(@class,'style_name__')]/text()")
#         additional_info = {label.strip(): value.strip() for label, value in zip(labels, values)}

#         def extract_detail(icon):
#             return tree.xpath(
#             f"string(//li[.//i[contains(@class,'{icon}')]]//div[contains(@class,'style_propInfodetailfigure__')]/span[1])"
#             ).strip()

#         bedrooms = extract_detail("icon-bedroom")
#         bathrooms = extract_detail("icon-bathroom")
#         living_room = extract_detail("icon-living-room")
#         land_area_info = extract_detail("icon-land-area")
        
#         data = {
#             "url": url,
#             "title": title,
#             "price": price,
#             "fal_license": fal_license,
#             "ref_no": ref_no,
#             "broker_name": broker_name,
#             "price_per_sqm": price_per_sqm,
#             "sale_status": sale_status,
#             "furnished_status": furnished_status,
#             "location": location,
#             "bedrooms": bedrooms,
#             "bathrooms": bathrooms,
#             "living_room": living_room,
#             "land_area": land_area_info or additional_info.get("Land area", ""),
#             "breadcrumbs": breadcrumbs,
#             "additional_info": additional_info,
#             "description": description,
#             "scraped_at": time.strftime("%Y-%m-%d"),
#         }

#         return data

#     def save(self, data):
#         if not self.target.find_one({"url": data["url"]}):
#             self.target.insert_one(data)
#             return True
#         return False

#     def run(self, limit=None):
#         urls = self.source.find().limit(limit) if limit else self.source.find()
#         for entry in urls:
#             try:
#                 content = self.fetch(entry["url"])
#                 data = self.parse_property(content, entry["url"])
#                 self.save(data)
#                 time.sleep(1)
#             except Exception as e:
#                 logging.error(e)

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     WasaltPropertyScraper().run()




#........................................................................................................................................................




import logging, time, requests
from parsel import Selector  # using Selector like template
from pymongo import MongoClient
from settings import MONGO_URI, DB_NAME, SOURCE_COLLECTION, TARGET_COLLECTION, HEADERS

class Parser:
    """Parser template for Wasalt property details"""

    def __init__(self):
        # queue and mongo connections as per template
        self.queue = None
        self.client = MongoClient(MONGO_URI)
        self.source = self.client[DB_NAME][SOURCE_COLLECTION]
        self.target = self.client[DB_NAME][TARGET_COLLECTION]

    def start(self, limit=None):
        """Start scraping from Mongo source collection"""

        # ########## used for queue-based crawling ##########
        # while True:
        #     url = self.queue.get()
        #     if not url:
        #         break
        # ########## used for queue-based crawling ##########

        metas = self.source.find().limit(limit) if limit else self.source.find()

        for meta in metas:
            url = meta.get("url")
            if not url:
                continue
            try:
                response = requests.get(url, headers=HEADERS, timeout=30)
                if response.status_code == 200:
                    self.parse_item(url, response.text)
                # else:
                #     self.queue.publish(url)  # requeue failed URL
            except Exception as e:
                logging.error(f"Request failed: {url} -> {e}")

    def close(self):
        """Close all connections"""
        self.client.close()
        # if self.queue:
        #     self.queue.close()

    def parse_item(self, url, html_content):
        """Parse property details"""
        sel = Selector(text=html_content)

        # XPaths (same structure as template)
        title = sel.xpath("string(//div[contains(@class,'stylenewPDP_pdpTitle__')])").get("").strip()
        price = sel.xpath("string(//div[contains(@class,'style_price__')])").get("").strip()
        tags = sel.xpath("//div[contains(@class,'style_pdpTagWrapper__')]/div/text()").getall()
        sale_status = tags[0].strip() if len(tags) > 0 else ""
        furnished_status = tags[1].strip() if len(tags) > 1 else ""

        location = " ".join([x.strip() for x in sel.xpath("//div[contains(@class,'stylenewPDP_propInfoAdd__')]//text()").getall() if x.strip()])

        breadcrumbs = " > ".join(sel.xpath(
            '//div[contains(@class,"stylenewPDP_breadcrumbsWrapper__")]//li//text()'
        ).getall()).strip()

        description = " ".join([p.strip() for p in sel.xpath(
            '//div[contains(@class,"style_pdpDescWrapper__")]//p/text()'
        ).getall() if p.strip()])

        fal_license = sel.xpath(
            "string(//div[contains(@class,'style_falLicense__')]//div[contains(@class,'style_value__')])"
        ).get("").strip()

        ref_no_text = sel.xpath(
            "string(//div[contains(@class,'style_refferenceNumberText__')]/span[1])"
        ).get("").strip()
        ref_no = ref_no_text.split()[-1] if ref_no_text else ""

        broker_name = sel.xpath(
            "string(//p[contains(@class,'style_brokerListedName__')])"
        ).get("").strip()

        area_price_number = sel.xpath(
            "string(//div[contains(@class,'style_areaDefine__')]/text())"
        ).get("").strip()
        area_price_unit = sel.xpath(
            "string(//div[contains(@class,'style_areaDefine__')]/span/text())"
        ).get("").strip()
        price_per_sqm = f"{area_price_number} {area_price_unit}".strip() if area_price_number else ""

        labels = sel.xpath(
            "//div[contains(@class,'style_infoSectionInnerContainer__')]//span[contains(@class,'style_infoLable__')]/text()"
        ).getall()
        values = sel.xpath(
            "//div[contains(@class,'style_infoSectionInnerContainer__')]//span[contains(@class,'style_name__')]/text()"
        ).getall()
        additional_info = {label.strip(): value.strip() for label, value in zip(labels, values)}

        def extract_detail(icon):
            return sel.xpath(
                f"string(//li[.//i[contains(@class,'{icon}')]]//div[contains(@class,'style_propInfodetailfigure__')]/span[1])"
            ).get("").strip()

        bedrooms = extract_detail("icon-bedroom")
        bathrooms = extract_detail("icon-bathroom")
        living_room = extract_detail("icon-living-room")
        land_area_info = extract_detail("icon-land-area")

        item = {
            "website": "Wasalt",
            "url": url,
            "title": title,
            "price": price,
            "fal_license": fal_license,
            "ref_no": ref_no,
            "broker_name": broker_name,
            "price_per_sqm": price_per_sqm,
            "sale_status": sale_status,
            "furnished_status": furnished_status,
            "location": location,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "living_room": living_room,
            "land_area": land_area_info or additional_info.get("Land area", ""),
            "breadcrumbs": breadcrumbs,
            "additional_info": additional_info,
            "description": description,
            "scraped_at": time.strftime("%Y-%m-%d"),
        }

        logging.info(item)

        try:
            if not self.target.find_one({"url": item["url"]}):
                self.target.insert_one(item)
        except Exception as e:
            logging.error(f"DB Insert Error: {url} -> {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = Parser()
    parser.start()
    parser.close()
