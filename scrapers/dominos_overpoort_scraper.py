import re
import time

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By

from data_types.choice import Choice, ChoiceList
from data_types.location import Location
from data_types.product import Product
from scrapers.scraper import Scraper

from seleniumbase import SB

from utils import comma_float


# sintp: "Konigin astridlaan 226, 9000 Gent",

class DominosOvpScraper(Scraper):

    @staticmethod
    def get_prices() -> (set[Product], Location):
        start_time = time.time()
        products = set()
        locatie = Location(
            "dominos_ovp: Dominos overpoort",
            "https://www.openstreetmap.org/node/5803560353",  # TODO not on openstreetmap
            "Bierkorfstraat 1, 9000 Gent",
            "092981999",
            "https://www.dominos.be/nl"
        )
        with (SB() as sb):
            # Open the menu page
            sb.open("https://www.dominos.be/nl/menu")
            # Wait for the input field with ID 'customer-suburb' to appear
            sb.wait_for_element('#customer-suburb', timeout=10)  # 10-second timeout

            # Clear the field before typing
            sb.clear('#customer-suburb')  # Clears any pre-existing value
            # Input '9000' into the field
            sb.type('#customer-suburb', 'gent dampoort', timeout=5)  # Using the SeleniumBase type() method

            sb.wait(3.0) # TODO make conditional
            # Wait until the "search-results" div is present
            sb.wait_for_element('.search-results', timeout=10)  # Adjust timeout if necessary

            # Find the first <a> tag inside the "search-results" div and click it
            search_results_div = sb.find_element('.search-results')  # Locate the div
            first_anchor_tag = search_results_div.find_element(By.TAG_NAME, 'a')  # Find the first <a> tag
            first_anchor_tag.click()  # Click the first <a> tag

            # Wait for the page to load completely
            sb.wait_for_element('.pizza-category', timeout=10)

            # Find all pizza-category divs
            pizza_categories = sb.find_elements('.pizza-category')

            # Iterate through each pizza-category div
            for category in pizza_categories:
                # Find all product-container divs within the category
                product_containers = category.find_elements(By.CLASS_NAME, 'product-container')

                for product in product_containers:
                    # Find the span with class menu-entry within each product-container
                    menu_entry = product.find_element(By.CLASS_NAME, 'menu-entry')
                    menu_entry_text = menu_entry.text

                    # Find the p with class menu-page-product-description
                    try:
                        product_description = product.find_element(By.CLASS_NAME, 'menu-page-product-description')
                        product_description_text = product_description.text
                    except Exception:
                        product_description_text = "(No description available)"

                    # Find the div with class product-price
                    try:
                        product_price = product.find_element(By.CLASS_NAME, 'product-price')
                        product_price_text = product_price.text
                        # Extract digits and commas using regex
                        price_digits = comma_float(re.sub(r"[^\d,]", "", product_price_text))
                    except Exception:
                        price_digits = 0.0

                    product = Product(name=menu_entry_text, description=product_description_text, price=price_digits)
                    # Print the menu entry and description
                    print(f"Menu Entry: {menu_entry_text}")
                    # print(f"Description: {product_description_text}")
                    # print(f"Price: {price_digits}")
                    products.add(product)

            # sb.wait(2000.0) #customer-suburb

        end_time = time.time()
        elapsed_time = end_time - start_time
        # Convert seconds to minutes and seconds
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        print(f"get_prices executed in {minutes} minute(s) and {seconds:.2f} second(s).")
        return products, locatie
