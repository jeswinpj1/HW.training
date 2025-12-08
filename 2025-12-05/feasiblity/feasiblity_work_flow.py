import re
import requests
from parsel import Selector
BASE_SITE = "https://www.lidl.co.uk"
HEADERS = {
    "Accept": "application/mindshift.search+json;version=2",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Referer": BASE_SITE + "/",
}

API_BASE = (
    "https://www.lidl.co.uk/q/api/search?"
    "offset=12&fetchsize=12&locale=en_GB&assortment=GB&version=2.1.0&category.id="
)

############################################################
#     CATEGORY ID EXTRACTION AND API URL GENERATION
############################################################
def fetch_category_ids():
    response = requests.get(BASE_SITE, headers=HEADERS)
    selector = Selector(response.text)

    links = selector.xpath('//a[contains(@class, "ACategoryOverviewSlider__Link")]/@href').getall()
        
    for link in links:
            match = re.search(r"s(\d+)", link)
            if match:
                f.write(match.group(1) + "\n")

def generate_api_urls():

        for category_id in map(str.strip, f_ids):
            api_url = API_BASE + category_id
            f_api.write(api_url + "\n")

############################################################
#                        CRAWLER
############################################################
class LidlCrawler:
    def start(self):
            for url in map(str.strip, file):
                if url:
                    self.fetch_products(url)

    def fetch_products(self, base_url):
        offset, page_size = 0, 12

        while True:
            api_url = re.sub(r"offset=\d+", f"offset={offset}", base_url)

            try:
                data = requests.get(api_url, headers=HEADERS, timeout=10).json()
            except Exception as e:
                break

            items = data.get("items", [])
            total = data.get("numFound") or data.get("keywordResults", {}).get("num_items_found", 0)
            for item in items:
                product = self.map_product(item)
                self.save_to_db(product)

            if offset >= total:
                break

    def map_product(self, p):
        grid = p.get("gridbox", {}).get("data", {})
        meta = p.get("gridbox", {}).get("meta", {})

        price = grid.get("price", {})
        lidl_plus = grid.get("lidlPlus", [])
        stock = grid.get("stockAvailability", {})
        badges = stock.get("badgeInfo", {}).get("badges", [])

        if lidl_plus:
            lp = lidl_plus[0]
            lp_price = lp.get("price", {}) or {}
            lp_discount = lp_price.get("discount", {}) or {}

            regular_price = (
                lp_discount.get("deletedPrice")
                or lp_price.get("deletedPrice")
                or lp_price.get("oldPrice")
                or price.get("oldPrice")
                or lp_discount.get("price")
                or price.get("price")
            )

            selling_price = (
                lp_price.get("price")
                or price.get("price")
                or self._extract_price_from_suffix(lp_price.get("suffix"))
            )

            promotion_type = "Lidl Plus"
            discount_text = lp_discount.get("discountText") or lp.get("highlightText", "")
            percentage_discount = lp_discount.get("percentageDiscount")

        elif "discount" in price:
            discount = price.get("discount", {})

            regular_price = (
                discount.get("deletedPrice")
                or discount.get("oldPrice")
                or price.get("oldPrice")
                or discount.get("price")
                or price.get("price")
            )

            selling_price = discount.get("price") or price.get("price")
            promotion_type = discount.get("discountText", "")
            discount_text = promotion_type
            percentage_discount = discount.get("percentageDiscount")
        else:
            regular_price = price.get("price")
            selling_price = regular_price
            promotion_type = ""
            discount_text = ""
            percentage_discount = None

        percent_match = re.search(r"(\d+%)", discount_text or "")
        percentage_discount = percent_match.group(1) if percent_match else ""

        currency = price.get("currencySymbol", "")

        breadcrumbs = meta.get("wonCategoryBreadcrumbs", [])
        names = [bc.get("name", "") for bc in (breadcrumbs[0] if breadcrumbs else [])]
        breadcrumb_full = " > ".join(names)

        levels = {f"producthierarchy_level{i+1}": names[i] if i < len(names) else "" for i in range(7)}
        instock = True
        if badges:
            text = badges[0].get("text", "").lower()
            typ = badges[0].get("type", "").upper()

            if text.startswith("in store from") or "FROM_FUTURE" in typ:
                instock = False
            elif "available in store now" in text or "PAST_DATE_RANGE" in typ or "IN_STORE_PAST" in typ:
                instock = True
            else:
                instock = ""

        elif stock.get("availabilityIndicator") is not None:
            instock = bool(int(stock["availabilityIndicator"]))

        return {
            "unique_id": str(p.get("code", "")),
            "product_unique_key": f"{p.get('code', '')}P",
            "brand": grid.get("brand", {}).get("name", ""),
            "category": grid.get("category", ""),
            "product_type": grid.get("productType", ""),
            "price_per_unit": price.get("basePrice", {}).get("text", ""),
            "product_name": grid.get("title", ""),
            "product_description": grid.get("keyfacts", {}).get("description", ""),
            "instock": instock,
            **levels,
            "breadcrumb": breadcrumb_full,
            "percentage_discount": percentage_discount,
            "regular_price": regular_price,
            "promotion_price": selling_price if promotion_type else None,
            "selling_price": selling_price,
            "promotion_type": promotion_type,
            "currency": currency,
            "pdp_url": BASE_SITE + grid.get("canonicalUrl", ""),
            "image_url_1": grid.get("imageList", [""])[0],
            "store_name": "Lidl",
            "extraction_date": "2025-10-27",
        }

    ####################################################
    #                 HELPER FUNCTIONS
    ####################################################
    def _extract_price_from_suffix(self, s):
        if not s:
            return None
        nums = re.findall(r"[\d.]+", s)
        return nums[0] if nums else None


####################################
#            findings 
####################################
# * the api has grenarated from catogary ids