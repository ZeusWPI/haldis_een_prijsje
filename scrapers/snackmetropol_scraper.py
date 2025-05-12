import time

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By

from data_types.choice import ChoiceList, Choice, ChoiceType
from data_types.location import Location
from data_types.product import Product, merge_products_by_sizes
from scrapers.scraper import Scraper

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
                # print(f"Clicked: {label.text}")

                sb.wait(2.0)  # TODO make conditional wait
                product_sections = sb.find_elements(".product-section.row-fluid")
                add_product_buttons = sb.find_elements("input.add-product-button")

                # Loop through each product section and extract the details
                for section, product_button in zip(product_sections, add_product_buttons):
                    try:
                        alles = section.text.split("\n")
                        # print(f"prod: {alles}")
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

                        max_retries = 3
                        for attempt in range(max_retries):
                            try:
                                product_button.click()
                                break
                            except StaleElementReferenceException:
                                if attempt < max_retries - 1:
                                    sb.wait(1)  # Wait before retrying
                                    product_button = sb.find_element("input.add-product-button")  # Refetch element
                                else:
                                    raise

                        print(f"clicked on {prod.name}")

                        # Wait for the variety selector to be visible
                        try:
                            sb.wait_for_element_visible("#food-variety-header-0",
                                                        timeout=10)
                        except Exception as e:
                            # sb.wait(2.0)
                            try:
                                sb.wait_for_element_visible("#food-variety-header-0",
                                                            timeout=10)
                            except Exception as e:
                                print(f"No variety components found for {prod.name}. Moving on...")
                                cancel_button = sb.find_element(".ui-dialog-titlebar-close", timout=20)

                                # Click the button
                                cancel_button.click()
                                sb.wait_for_element_not_visible("#ui-widget-overlay ui-front", timeout=10)
                                products.add(prod)
                                continue

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

                                    # Stop if the element's content is exactly "meer"
                                    if element_text.strip().lower() == "meer":
                                        break

                                    component_ids.append(element_id)  # Add to the list
                                    x += 1  # Increment to check the next ID
                                else:
                                    break  # Stop the loop if the element is not found
                            except Exception as e:
                                break  # Stop the loop on any unexpected issue
                        if not component_ids:
                            print(f"No components found for {prod}")
                        # print(f"{component_ids=}")
                        for index, element in enumerate(component_ids):
                            sb.wait_for_element_visible(f"#{element}")
                            sb.click(f"#{element}")
                            sb.wait_for_element_visible(f"#ui-accordion-accordion-panel-{index}")
                            keuzelijst = ChoiceList(
                                name=sb.get_text(f"#food-variety-header-{index}").strip(),
                                description="Welke " + sb.get_text(f"#food-variety-header-{index}").strip(),
                                type=ChoiceType.MULTI
                            )
                            # Locate the main div by ID
                            parent_div_id = f"ui-accordion-accordion-panel-{index}"
                            child_divs = sb.find_elements(f"#{parent_div_id} > div")  # Direct child <div>s

                            is_multi_choice = any(
                                div.find_elements("css selector", "input[type='checkbox']") for div in child_divs
                            )
                            keuzelijst.multi_choice = is_multi_choice

                            # Iterate over each child div and extract text from the first span
                            for child_div in child_divs:
                                max_retries = 6  # Set the maximum number of retries
                                retry_count = 0

                                spans = child_div.find_elements("tag name",
                                                                "span")  # Find all <span> elements inside the child div
                                span_contents = [span.text for span in
                                                 spans]  # Extract text from each span and store it in a list

                                # Retry loop if all spans are empty
                                while (
                                       len(span_contents) != 3 or span_contents[0] == "" or
                                       all( content == "" for content in span_contents) or
                                       span_contents[2] == "" and span_contents[1] != ""
                                ) and retry_count < max_retries:
                                    print(f"{span_contents}, retrying (attempt {retry_count + 1})...")
                                    retry_count += 1
                                    # Wait or perform an action to try again (for example, wait for a new state or
                                    # refresh the page)
                                    sb.wait(0.5)  # Adjust wait time as needed
                                    spans = child_div.find_elements("tag name", "span")  # Re-fetch the spans
                                    span_contents = [span.text for span in spans]  # Extract the new text from the spans

                                # print(f"Spans in child div: {span_contents}")
                                # print(f"choice: {text}")
                                if span_contents[1] == "":
                                    keuzelijst.add_choice(Choice(name=span_contents[0]))
                                elif span_contents[1].startswith("€"):
                                    keuzelijst.add_choice(
                                        Choice(
                                            name=span_contents[0],
                                            price=float(span_contents[2].replace(",", "."))
                                        )
                                    )
                                else:
                                    try:
                                        keuzelijst.add_choice(Choice(name=span_contents[0]))
                                    except Exception as e:
                                        print("errored on: " + str(span_contents))
                            prod.add_choiceList(keuzelijst)
                        # Find the button with the class name "select-variety-btn btn"
                        cancel_button = sb.find_element(".ui-dialog-titlebar-close")

                        # Click the button
                        cancel_button.click()
                        sb.wait_for_element_not_visible("#ui-widget-overlay ui-front", timeout=10)
                        # print("not found end")
                        products.add(prod)
                    except Exception as e:
                        print(f"Error extracting product information: {e}")

        # merge products of different sizes
        # TODO some products have other options small and large
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

        end_time = time.time()
        elapsed_time = end_time - start_time
        # Convert seconds to minutes and seconds
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        print(f"get_prices executed in {minutes} minute(s) and {seconds:.2f} second(s).")
        return products, locatie
