from bs4 import BeautifulSoup

from data_types.location import Location
from data_types.product import Product
from scrapers.scraper import Scraper
from utils import safe_get


class MetropolScraper(Scraper):

    @staticmethod
    def get_prices() -> (set[Product], Location):

        base_url = "https://snackmetropol.be/Menu/Menu/ProductsByCategory?categoryId="
        # URL of the webpage you want to extract HTML from
        extra_url_s = [
            "25472&_=1728579094939",
            "25473&_=1728579094940",
            "25474&_=1728580943523",
            "25475&_=1728580943524",
            "25476&_=1728580943525",
            "25478&_=1728580943526",
            "25480&_=1728580943529",
            "25481&_=1728580943530",
            "25755&_=1728580943531",
            "34984&_=1728580943532",
            "42886&_=1728580943533"
        ]

        products = set()
        locatie = Location(
            "metropol: Metropol",
            "https://www.openstreetmap.org/search?lat=51.022479&lon=3.720194#map=19/51.022481/3.720194",
            "Zwijnaardsesteenweg 662, 9000 Gent",
            "0491 11 04 13",
            "https://snackmetropol.be/"
        )

        for link in extra_url_s:
            # Send a GET request to the webpage
            full_link = base_url + link
            # print(full_link)
            response = safe_get(full_link)
            if response == "":
                return set(), locatie

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # # Get the entire HTML content
            # html_content = soup.prettify()
            #
            # # Print or save the HTML content
            # print(html_content)

            # Find all divs with class 'product-prices span3'
            divs = soup.find_all('div', class_='product-section row-fluid')

            # Print the found divs
            for div in divs:
                # print(div.prettify())
                product = Product()
                # Find and print the 'p' tag with class 'product-name'
                product_name = div.find('p', class_='product-name')
                if product_name:
                    product.name = product_name.get_text().strip()

                # Find and print the 'span' tag with class 'product-price'
                product_price = div.find('span', class_='product-price')
                if product_price:
                    product.price = product_price.get_text().strip().split(" ")[-1].replace(',', '.')
                # print(product)
                products.add(product)

        return products, locatie
