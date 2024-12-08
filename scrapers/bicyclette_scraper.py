import time

from data_types.choice import ChoiceList, Choice
from data_types.location import Location
from data_types.product import Product
from scrapers.scraper import Scraper
from utils import extract_spans, filter_divs, create_heading_contains_h2_with, fetch_and_parse_html


class BicycletteScraper(Scraper):
    @staticmethod
    def get_prices() -> (set[Product], Location):
        start_time = time.time()
        base_url = "https://labicyclettepastabar.be/menu/"

        products = set()
        locatie = Location(
            "bicyclette: Bicyclette",
            "https://www.openstreetmap.org/node/9787361791#map=19/51.030240/3.706148",
            "Voskenslaan 187, 9000 Gent",
            "+32 468 13 09 20",
            "https://labicyclettepastabar.be/"
        )

        soup = fetch_and_parse_html(base_url)
        if not soup:
            return set(), locatie

        # Filter out the divs that contain a specific child div
        filtered_divs = filter_divs(soup, 'elementor-widget-wrap elementor-element-populated',
                                    create_heading_contains_h2_with("Pasta's"))

        # Find all top-level divs in the first filtered div
        if filtered_divs:
            first_filtered_div = filtered_divs[0]
            top_level_divs = first_filtered_div.find_all(recursive=False)  # Only direct children
            for div in top_level_divs:
                span_texts = extract_spans(div)
                # print(span_texts)
                if len(span_texts) == 2:
                    products.add(Product(name=span_texts[0], description=span_texts[1]))
                if len(span_texts) == 3:
                    products.add(Product(name=span_texts[0], description=span_texts[2]))
        else:
            print("No pastas divs found.")

        filtered_divs = filter_divs(soup, 'elementor-widget-wrap elementor-element-populated',
                                    create_heading_contains_h2_with("Prijzen"))

        first_filtered_div = filtered_divs[0]
        size_choice_list = ChoiceList()
        keuzes = []
        min_price = 6.0
        if filtered_divs:
            prijzen_div = first_filtered_div.find_all(class_ = "elementor-element elementor-element-15aaf55 elementor-widget elementor-widget-text-editor")
            span_texts = extract_spans(prijzen_div[0])
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
            span_texts = extract_spans(extra_div[0])
            span_texts = [text.strip().split(": € ") for text in span_texts]

            for ell in span_texts:
                products.add(Product(name=ell[0].strip(), price=float(ell[1].strip().replace(",", "."))))
        else:
            print("No extra divs found.")

        end_time = time.time()
        elapsed_time = end_time - start_time
        # Convert seconds to minutes and seconds
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        print(f"get_prices executed in {minutes} minute(s) and {seconds:.2f} second(s).")
        return products, locatie
