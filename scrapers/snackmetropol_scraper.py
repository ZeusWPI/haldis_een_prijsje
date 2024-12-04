from bs4 import BeautifulSoup

from data_types.common_choice_lists import (create_metropol_vlees_keuze_list, create_metropol_sauzen_keuze_list,
                                            create_metropol_groenten_keuze_list, create_metropol_extra_keuze_list)
from data_types.location import Location
from data_types.product import Product, add_choiseList_to_product_by_name, merge_products
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

        # merge products of different sizes
        products = merge_products(
            products,
            ["BROODJE FALAFEL KLEIN", "BROODJE FALAFEL GROOT"],
            "BROODJE FALAFEL",
            ["klein", "groot"]
        )

        products = merge_products(
            products,
            ["Pita klein", "Pita groot"],
            "Pita",
            ["klein", "groot"]
        )

        products = merge_products(
            products,
            ["Broodje Kapsalon klein", "Broodje Kapsalon groot"],
            "Broodje Kapsalon",
            ["klein", "groot"]
        )

        products = merge_products(
            products,
            ["DURUM KLEIN", "Durum"],
            "Durum",
            ["klein", "groot"]
        )

        products = merge_products(
            products,
            ["Schotel klein", "Schotel groot"],
            "Schotel",
            ["klein", "groot"]
        )

        products = merge_products(
            products,
            ["Hamburgerschotel", "Hamburgerschotel Groot"],
            "Hamburgerschotel",
            ["klein", "groot"]
        )

        products = merge_products(
            products,
            ["frikandelschotel", "frikandelschotel groot"],
            "frikandelschotel",
            ["klein", "groot"]
        )

        products = merge_products(
            products,
            ["Kapsalon klein", "Kapsalon groot"],
            "Kapsalon",
            ["klein", "groot"]
        )

        products = merge_products(
            products,
            ["Frietjes klein", "Frietjes medium", "Frietjes groot", "Frietjes familie"],
            "Frietjes",
            ["klein", "medium", "groot", "familie"]
        )

        # add keuzes
        vlees_keuze_list = create_metropol_vlees_keuze_list()
        saus_keuze_list = create_metropol_sauzen_keuze_list()
        groenten_keuze_list = create_metropol_groenten_keuze_list()
        extra_keuze_list = create_metropol_extra_keuze_list()
        # Map products to choice lists
        product_choices = {
            vlees_keuze_list: [
                "Pita", "Durum",
                "Broodje Kapsalon",
                "Lachmacun Delux",
                "BROODJE FALAFEL", "Schotel", "Ayoubschotel", "Hamburgerschotel",
                "frikandelschotel", "Kapsalon", "GRILL MIXXL", "Nieuw Product",
                "Taco", "TACO SNACK"
            ],
            saus_keuze_list: [
                "Pita", "Durum",
                "Broodje Kapsalon",
                "Lahmacun", "Lachmacun Delux",
                "BROODJE FALAFEL",
                "Dubbele Franse Hamburger", "Franse Hamburger", "Schotel", "Ayoubschotel",
                "Hamburgerschotel", "frikandelschotel", "Kapsalon", "GRILL MIXXL",
                "Nieuw Product", "bickyburger", "cheesburger", "vishburger", "kipburger",
                "broodjemexicano +friet", "Taco", "TACO SNACK", "Potje"
            ],
            groenten_keuze_list: [
                "Pita", "Durum",
                "Broodje Kapsalon",
                "Lahmacun", "Lachmacun Delux",
                "BROODJE FALAFEL",
                "Dubbele Franse Hamburger", "Franse Hamburger", "Schotel", "Ayoubschotel",
                "Hamburgerschotel", "frikandelschotel", "Kapsalon", "GRILL MIXXL",
                "Nieuw Product", "bickyburger", "cheesburger", "vishburger", "kipburger",
                "broodjemexicano +friet", "Taco", "TACO SNACK"
            ],
            extra_keuze_list: [
                "Pita", "Durum",
                "Broodje Kapsalon",
                "Lahmacun", "Lachmacun Delux",
                "BROODJE FALAFEL",
                "Dubbele Franse Hamburger", "Franse Hamburger", "Schotel", "Ayoubschotel",
                "Hamburgerschotel", "frikandelschotel", "Kapsalon", "GRILL MIXXL",
                "Nieuw Product", "bickyburger", "cheesburger", "vishburger", "kipburger",
                "broodjemexicano +friet", "Taco", "TACO SNACK"
            ]
        }

        # Add choice lists to products
        for choice_list, product_names in product_choices.items():
            add_choiseList_to_product_by_name(products, choice_list, product_names)

        return products, locatie
