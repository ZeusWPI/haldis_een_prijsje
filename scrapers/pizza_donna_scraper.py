import time

from data_types.choice import ChoiceList, Choice
from data_types.location import Location
from data_types.product import Product
from scrapers.scraper import Scraper
from utils import filter_divs, fetch_and_parse_html, condition_has_text, get_non_empty_p_texts, comma_float


def add_products_from_selected_p_div_index(products, p_div_index, filtered_divs):
    selected_p_texts = get_non_empty_p_texts(filtered_divs[p_div_index])
    for i in range(0, len(selected_p_texts)):
        products.add(
            Product(
                name=" ".join(selected_p_texts[i].split(" ")[:-1]).strip(),
                price=comma_float(selected_p_texts[i].split(" ")[-1])
            )
        )
    return products


class PizzaDonnaScraper(Scraper):
    @staticmethod
    def get_prices() -> (set[Product], Location):
        start_time = time.time()
        base_url = "https://primadonnagent.be/Menu"

        products = set()
        locatie = Location(
            "pizza_donna: Pizza Donna",
            "https://www.openstreetmap.org/way/498363815#map=19/51.040288/3.725639",
            "Overpoortstraat 46, 9000 Gent",
            "+32 (0)475 40 13 00",
            "https://primadonnagent.be/"
        )

        soup = fetch_and_parse_html(base_url)
        if not soup:
            return set(), locatie

        # Filter out the divs that contain a specific child div
        filtered_divs = filter_divs(soup, "Preview_row__3Fkye row",
                                    condition_has_text)
        pizza_p_texts = get_non_empty_p_texts(filtered_divs[2])
        for i in range(0, len(pizza_p_texts) - 8, 2):  # TODO parse de laatste 8 appart (de fantaseer zelf)
            if pizza_p_texts[i].split(" ")[-2] == "-":
                from_price = comma_float(pizza_p_texts[i].split(" ")[-3])
                to_price = comma_float(pizza_p_texts[i].split(" ")[-1])
                product = Product(
                    name=" ".join(pizza_p_texts[i].split(" ")[:-3]),
                    description=pizza_p_texts[i + 1],
                    price=from_price
                )

                groote_keuze = ChoiceList(  # TODO check what the from to prices actually mean
                    name="what size?",
                    choices=[
                        Choice(name="small", price=0.0),
                        Choice(
                            name="medium",
                            price=to_price - from_price
                        )
                    ]
                )
                product.add_choiceList(groote_keuze)
                products.add(product)

            else:
                from_price = comma_float(pizza_p_texts[i].split(" ")[-2][:-1])
                to_price = comma_float(pizza_p_texts[i].split(" ")[-1])
                product = Product(
                    name=" ".join(pizza_p_texts[i].split(" ")[:-2]),
                    description=pizza_p_texts[i + 1],
                    price=from_price
                )

                groote_keuze = ChoiceList(  # TODO check what the from to prices actually mean
                    name="what size?",
                    choices=[
                        Choice(name="small", price=0.0),
                        Choice(
                            name="medium",
                            price=to_price - from_price
                        )
                    ]
                )
                product.add_choiceList(groote_keuze)
                products.add(product)
        products = add_products_from_selected_p_div_index(products, 4, filtered_divs)
        products = add_products_from_selected_p_div_index(products, 6, filtered_divs)
        products = add_products_from_selected_p_div_index(products, 8, filtered_divs)
        products = add_products_from_selected_p_div_index(products, 10, filtered_divs)
        # products = add_products_from_selected_p_div_index(products, 12, filtered_divs) #  TODO skipped alcoholishe dranken
        products = add_products_from_selected_p_div_index(products, 14, filtered_divs)

        end_time = time.time()
        elapsed_time = end_time - start_time
        # Convert seconds to minutes and seconds
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        print(f"get_prices executed in {minutes} minute(s) and {seconds:.2f} second(s).")
        return products, locatie
