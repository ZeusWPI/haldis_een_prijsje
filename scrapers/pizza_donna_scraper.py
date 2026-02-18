import time

from data_types.choice import ChoiceList, Choice
from data_types.location import Location
from data_types.product import Product
from scrapers.scraper import Scraper
from utils import fetch_and_parse_html


class PizzaDonnaScraper(Scraper):
    @staticmethod
    def get_prices() -> (set[Product], Location):
        start_time = time.time()
        base_url = "https://primadonnagent.be/"
        extras = ["pizza/", "calzone/", "pasta/", "broodjes/", "dessert/", "frisdranken/", "bieren/", "aperitieven/", "warme-dranken/"]
        # TODO wijnen/ skipped
        products = set()
        locatie = Location(
            "pizza_donna: Pizza Donna",
            "https://www.openstreetmap.org/way/498363815#map=19/51.040288/3.725639",
            "Overpoortstraat 46, 9000 Gent",
            "+32 (0)475 40 13 00",
            "https://primadonnagent.be/"
        )
        for extr in extras:
            soup = fetch_and_parse_html(base_url + extr)
            if not soup:
                return set(), locatie
            category_ul = soup.find_all("ul")[3]
            for item_li in category_ul.find_all("li"):
                title = item_li.find("h2").text
                descr = item_li.find("p").text if item_li.find("p") else ""
                title, price = title.split("€")
                product = Product(
                    name=title,
                    description=descr,
                    price=price
                )
                products.add(product)
        return products, locatie
    
