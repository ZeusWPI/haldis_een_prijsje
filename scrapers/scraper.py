from data_types.product import Product


class Scraper:
    @staticmethod
    def get_prices() -> set[Product]:
        raise NotImplementedError("Subclasses must implement parse_prices method.")
