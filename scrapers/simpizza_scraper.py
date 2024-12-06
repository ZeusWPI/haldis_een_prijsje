import time

from selenium.webdriver.common.by import By

from data_types.choice import Choice, ChoiceList
from data_types.location import Location
from data_types.product import Product
from scrapers.scraper import Scraper

from seleniumbase import SB


# https://www.simpizza.be/Menu
class SimpizzaScraper(Scraper):

    @staticmethod
    def get_prices() -> (set[Product], Location):
        start_time = time.time()
        products = set()
        locatie = Location(
            "simpizza: Simpizza",
            "https://www.openstreetmap.org/node/5803560353",
            "De Pintelaan 252, 9000 Gent",
            "+32 9 321 02 00",
            "https://www.simpizza.be/"
        )
        with SB() as sb:
            # Open the menu page
            sb.open("https://www.simpizza.be/Menu")

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
