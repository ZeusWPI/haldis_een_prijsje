from data_types.product import Product
from data_types.location import Location


class Scraper:
    @staticmethod
    def get_prices() -> (set[Product], Location):
        raise NotImplementedError("Subclasses must implement parse_prices method.")
