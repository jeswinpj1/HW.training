
class PropertyURL:
    def __init__(self, url: str):
        self.url = url


class PropertyDetails:
    def __init__(self, url, title, price, location, bedrooms, land_area,
                 breadcrumbs, additional_info, description, scraped_at):
        self.url = url
        self.title = title
        self.price = price
        self.location = location
        self.bedrooms = bedrooms
        self.land_area = land_area
        self.breadcrumbs = breadcrumbs
        self.additional_info = additional_info
        self.description = description
        self.scraped_at = scraped_at

    def to_dict(self):
        return self.__dict__
