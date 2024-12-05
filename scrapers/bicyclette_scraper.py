from bs4 import BeautifulSoup

from data_types.choice import ChoiceList, Choice, ChoiceType
from data_types.common_choice_lists import (create_metropol_vlees_keuze_list, create_metropol_sauzen_keuze_list,
                                            create_metropol_groenten_keuze_list, create_metropol_extra_keuze_list)
from data_types.location import Location
from data_types.product import Product, add_choiseList_to_product_by_name, merge_products
from scrapers.scraper import Scraper
from utils import safe_get


class BicycletteScraper(Scraper):
    @staticmethod
    def get_prices() -> (set[Product], Location):

        base_url = "https://labicyclettepastabar.be/menu/"

        products = set()
        locatie = Location(
            "bicyclette: Bicyclette",
            "https://www.openstreetmap.org/node/9787361791#map=19/51.030240/3.706148",
            "Voskenslaan 187, 9000 Gent",
            "+32 468 13 09 20",
            "https://labicyclettepastabar.be/"
        )

        response = safe_get(base_url)
        if response == "":
            return set(), locatie

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all divs with class 'product-prices span3'
        canidate_divs = soup.find_all('div', class_=
            'elementor-widget-wrap elementor-element-populated')

        # Filter out the divs that contain a specific child div
        filtered_divs = []
        for parent in canidate_divs:
            h2_tag = parent.find('div', class_='elementor-widget-container').find('h2', string=lambda text: "Pasta's" in text if text else False)
            if h2_tag:
                filtered_divs.append(parent)

        # Find all top-level divs in the first filtered div
        if filtered_divs:
            first_filtered_div = filtered_divs[0]
            top_level_divs = first_filtered_div.find_all(recursive=False)  # Only direct children
            for div in top_level_divs:
                spans = div.find_all('span', string=lambda text: text and text.strip())  # Collect spans from each top-level div
                span_texts = [span.text.strip() for span in spans]
                if len(span_texts) == 2:
                    products.add(Product(name=span_texts[0], description=span_texts[1]))
        else:
            print("No pastas divs found.")

        filtered_divs = []
        for parent in canidate_divs:
            h2_tag = parent.find('div', class_='elementor-widget-container').find('h2', string=lambda text: "Prijzen" in text if text else False)
            if h2_tag:
                filtered_divs.append(parent)

        first_filtered_div = filtered_divs[0]
        size_choice_list = ChoiceList()
        keuzes = []
        min_price = 6.0
        if filtered_divs:
            prijzen_div = first_filtered_div.find_all(class_ = "elementor-element elementor-element-15aaf55 elementor-widget elementor-widget-text-editor")
            spans = prijzen_div[0].find_all('span', string=lambda text: text and text.strip())  # Collect spans from each top-level div
            span_texts = [span.text.strip() for span in spans]
            keuzes.append(Choice(span_texts[0][:-1].strip(), 0.0))
            min_price = float(span_texts[1].strip()[2:].replace(",", "."))

            for i in range(2, len(span_texts), 2):
                keuzes.append(Choice(span_texts[i][:-1].strip(), float(span_texts[i+1].strip()[2:].replace(",", "."))-min_price))
        else:
            print("No prijzen divs found.")
        size_choice_list.choices = keuzes

        # Add choice lists to products
        for product in products:
            product.add_choiceList(size_choice_list)
            product.price = min_price

        if filtered_divs:
            extra_div = first_filtered_div.find_all(class_ = "elementor-element elementor-element-a896b7f elementor-widget elementor-widget-text-editor")
            spans = extra_div[0].find_all('span', string=lambda text: text and text.strip())  # Collect spans from each top-level div
            span_texts = [span.text.strip() for span in spans]

            span_texts = [text.strip().split(": € ") for text in span_texts]

            for ell in span_texts:
                products.add(Product(name=ell[0].strip(), price=float(ell[1].strip().replace(",", "."))))
        else:
            print("No extra divs found.")

        return products, locatie
