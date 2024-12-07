import time

from selenium.webdriver.common.by import By

from data_types.choice import ChoiceList, Choice
from data_types.common_choice_lists import (create_metropol_vlees_keuze_list, create_metropol_sauzen_keuze_list,
                                            create_metropol_groenten_keuze_list, create_metropol_extra_keuze_list)
from data_types.location import Location
from data_types.product import Product, add_choiseList_to_product_by_name, merge_products, merge_products_by_sizes
from scrapers.scraper import Scraper
from utils import fetch_and_parse_html

from seleniumbase import SB


class MetropolScraper(Scraper):

    @staticmethod
    def get_prices() -> (set[Product], Location):
        start_time = time.time()
        products = set()
        locatie = Location(
            "metropol: Metropol",
            "https://www.openstreetmap.org/search?lat=51.022479&lon=3.720194#map=19/51.022481/3.720194",
            "Zwijnaardsesteenweg 662, 9000 Gent",
            "0491 11 04 13",
            "https://snackmetropol.be/"
        )

        with SB() as sb:
            # Open the menu page
            sb.open("https://snackmetropol.be/Menu")

            # Find the div with class 'categories-listed'
            categories_div = sb.find_element(".categories-listed")

            # Find all labels inside this div
            labels = categories_div.find_elements(By.TAG_NAME, "label")

            # Loop through the labels and print their text
            for label in labels:
                label.click()  # Click the label
                print(f"Clicked: {label.text}")

                sb.wait(1.0)
                product_sections = sb.find_elements(".product-section.row-fluid")
                add_product_buttons = sb.find_elements("input.add-product-button")

                # Loop through each product section and extract the details
                for section, product_button in zip(product_sections, add_product_buttons):
                    try:
                        alles = section.text.split("\n")
                        # print(section.text.split("\n"))
                        if len(alles) == 3:
                            prod = Product(
                                name=alles[0].strip(),
                                description=alles[1].strip(),
                                price=float(alles[2].split(" ")[1].replace(",", "."))
                            )
                        elif len(alles) == 2:
                            prod = Product(
                                name=alles[0].strip(),
                                price=float(alles[1].split(" ")[1].replace(",", "."))
                            )
                        else:
                            print("Invalid")
                        # print(prod)
                        product_button.click()

                        # Wait for the variety selector to be visible
                        sb.wait(1.0)

                        # Extract selected options and their prices from `product-item-list`
                        # Initialize an empty list to store the IDs
                        component_ids = []

                        # Start iterating with `x = 0`
                        x = 0
                        while True:
                            try:
                                # Construct the ID dynamically
                                element_id = f"food-variety-header-{x}"

                                # Check if the element exists
                                if sb.is_element_visible(f"#{element_id}"):
                                    element_text = sb.get_text(f"#{element_id}")  # Get the text of the element

                                    # Stop if the element's content is exactly "Meer"
                                    if element_text.strip().lower() == "meer":
                                        break

                                    component_ids.append(element_id)  # Add to the list
                                    x += 1  # Increment to check the next ID
                                else:
                                    break  # Stop the loop if the element is not found
                            except Exception as e:
                                break  # Stop the loop on any unexpected issue
                        # print(f"{component_ids=}")
                        for index, element in enumerate(component_ids):
                            sb.wait_for_element_visible(f"#{element}")
                            sb.click(f"#{element}")
                            sb.wait_for_element_visible(f"#ui-accordion-accordion-panel-{index}")
                            keuzelijst = ChoiceList(
                                name=sb.get_text(f"#food-variety-header-{index}").strip(),
                                description="Welke " + sb.get_text(f"#food-variety-header-{index}").strip()
                            )
                            # Locate the main div by ID
                            parent_div_id = f"ui-accordion-accordion-panel-{index}"
                            child_divs = sb.find_elements(f"#{parent_div_id} > div")  # Direct child <div>s

                            # Iterate over each child div and extract text from the first span
                            for child_div in child_divs:
                                text = child_div.text.split("\n")
                                if len(text) == 1:
                                    keuzelijst.add_choice(Choice(name=text[0]))
                                elif len(text) == 2:
                                    if text[1].startswith("€"):
                                        keuzelijst.add_choice(
                                            Choice(
                                                name=text[0],
                                                price=float(text[1].split("+")[1].replace(",", "."))
                                            )
                                        )
                                    else:
                                        keuzelijst.add_choice(Choice(name=text[0]))
                                else:
                                    print("errored on: " + text)
                            prod.add_choiceList(keuzelijst)
                        # Find the button with the class name "select-variety-btn btn"
                        cancel_button = sb.find_element(".ui-dialog-titlebar-close")

                        # Click the button
                        cancel_button.click()
                        products.add(prod)
                    except Exception as e:
                        print(f"Error extracting product information: {e}")

        end_time = time.time()
        elapsed_time = end_time - start_time
        # Convert seconds to minutes and seconds
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        print(f"get_prices executed in {minutes} minute(s) and {seconds:.2f} second(s).")
        return products, locatie







        # base_url = "https://snackmetropol.be/Menu/Menu/ProductsByCategory?categoryId="
        # # URL of the webpage you want to extract HTML from
        # extra_url_s = [
        #     "25472&_=1728579094939",
        #     "25473&_=1728579094940",
        #     "25474&_=1728580943523",
        #     "25475&_=1728580943524",
        #     "25476&_=1728580943525",
        #     "25478&_=1728580943526",
        #     "25480&_=1728580943529",
        #     "25481&_=1728580943530",
        #     "25755&_=1728580943531",
        #     "34984&_=1728580943532",
        #     "42886&_=1728580943533"
        # ]
        #
        # products = set()
        # locatie = Location(
        #     "metropol: Metropol",
        #     "https://www.openstreetmap.org/search?lat=51.022479&lon=3.720194#map=19/51.022481/3.720194",
        #     "Zwijnaardsesteenweg 662, 9000 Gent",
        #     "0491 11 04 13",
        #     "https://snackmetropol.be/"
        # )
        #
        # for link in extra_url_s:
        #     # Send a GET request to the webpage
        #     full_link = base_url + link
        #     # print(full_link)
        #     soup = fetch_and_parse_html(full_link)
        #     if not soup:
        #         print("Skipping " + full_link)
        #         continue
        #
        #     # Find all divs with class 'product-prices span3'
        #     divs = soup.find_all('div', class_='product-section row-fluid')
        #
        #     # Print the found divs
        #     for div in divs:
        #         # print(div.prettify())
        #         product = Product()
        #         # Find and print the 'p' tag with class 'product-name'
        #         product_name = div.find('p', class_='product-name')
        #         if product_name:
        #             product.name = product_name.get_text().strip()
        #
        #         # Find and print the 'span' tag with class 'product-price'
        #         product_price = div.find('span', class_='product-price')
        #         if product_price:
        #             product.price = product_price.get_text().strip().split(" ")[-1].replace(',', '.')
        #         # print(product)
        #         products.add(product)
        #
        # # merge products of different sizes
        # merge_specs = [
        #     (["BROODJE FALAFEL KLEIN", "BROODJE FALAFEL GROOT"], "BROODJE FALAFEL", ["klein", "groot"]),
        #     (["Pita klein", "Pita groot"], "Pita", ["klein", "groot"]),
        #     (["Broodje Kapsalon klein", "Broodje Kapsalon groot"], "Broodje Kapsalon", ["klein", "groot"]),
        #     (["DURUM KLEIN", "Durum"], "Durum", ["klein", "groot"]),
        #     (["Schotel klein", "Schotel groot"], "Schotel", ["klein", "groot"]),
        #     (["Hamburgerschotel", "Hamburgerschotel Groot"], "Hamburgerschotel", ["klein", "groot"]),
        #     (["frikandelschotel", "frikandelschotel groot"], "frikandelschotel", ["klein", "groot"]),
        #     (["Kapsalon klein", "Kapsalon groot"], "Kapsalon", ["klein", "groot"]),
        #     (["Frietjes klein", "Frietjes medium", "Frietjes groot", "Frietjes familie"], "Frietjes", ["klein", "medium", "groot", "familie"])
        # ]
        # products = merge_products_by_sizes(products, merge_specs)
        #
        # # add keuzes
        # vlees_keuze_list = create_metropol_vlees_keuze_list()
        # saus_keuze_list = create_metropol_sauzen_keuze_list()
        # groenten_keuze_list = create_metropol_groenten_keuze_list()
        # extra_keuze_list = create_metropol_extra_keuze_list()
        # # Map products to choice lists
        # product_choices = {
        #     vlees_keuze_list: [
        #         "Pita", "Durum",
        #         "Broodje Kapsalon",
        #         "Lachmacun Delux",
        #         "BROODJE FALAFEL", "Schotel", "Ayoubschotel", "Hamburgerschotel",
        #         "frikandelschotel", "Kapsalon", "GRILL MIXXL", "Nieuw Product",
        #         "Taco", "TACO SNACK"
        #     ],
        #     saus_keuze_list: [
        #         "Pita", "Durum",
        #         "Broodje Kapsalon",
        #         "Lahmacun", "Lachmacun Delux",
        #         "BROODJE FALAFEL",
        #         "Dubbele Franse Hamburger", "Franse Hamburger", "Schotel", "Ayoubschotel",
        #         "Hamburgerschotel", "frikandelschotel", "Kapsalon", "GRILL MIXXL",
        #         "Nieuw Product", "bickyburger", "cheesburger", "vishburger", "kipburger",
        #         "broodjemexicano +friet", "Taco", "TACO SNACK", "Potje"
        #     ],
        #     groenten_keuze_list: [
        #         "Pita", "Durum",
        #         "Broodje Kapsalon",
        #         "Lahmacun", "Lachmacun Delux",
        #         "BROODJE FALAFEL",
        #         "Dubbele Franse Hamburger", "Franse Hamburger", "Schotel", "Ayoubschotel",
        #         "Hamburgerschotel", "frikandelschotel", "Kapsalon", "GRILL MIXXL",
        #         "Nieuw Product", "bickyburger", "cheesburger", "vishburger", "kipburger",
        #         "broodjemexicano +friet", "Taco", "TACO SNACK"
        #     ],
        #     extra_keuze_list: [
        #         "Pita", "Durum",
        #         "Broodje Kapsalon",
        #         "Lahmacun", "Lachmacun Delux",
        #         "BROODJE FALAFEL",
        #         "Dubbele Franse Hamburger", "Franse Hamburger", "Schotel", "Ayoubschotel",
        #         "Hamburgerschotel", "frikandelschotel", "Kapsalon", "GRILL MIXXL",
        #         "Nieuw Product", "bickyburger", "cheesburger", "vishburger", "kipburger",
        #         "broodjemexicano +friet", "Taco", "TACO SNACK"
        #     ]
        # }
        #
        # # Add choice lists to products
        # for choice_list, product_names in product_choices.items():
        #     add_choiseList_to_product_by_name(products, choice_list, product_names)
        #
        # return products, locatie
