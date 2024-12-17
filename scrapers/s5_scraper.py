import json
import time
from datetime import datetime

import requests

from data_types.choice import ChoiceList, Choice
from data_types.location import Location
from data_types.product import Product
from scrapers.scraper import Scraper
from utils import extract_spans, filter_divs, create_heading_contains_h2_with, fetch_and_parse_html, comma_float


class S5Scraper(Scraper):
    @staticmethod
    def get_prices() -> (set[Product], Location):
        start_time = time.time()

        products = set()
        locatie = Location(
            "s5: S5",
            "https://www.openstreetmap.org/node/2659815473",
            "Krijgslaan 281, 9000 Gent",
            "+32 000 00 00 00",  # TODO not found
            "https://www.ugent.be/student/nl/meer-dan-studeren/resto/restos/restocampussterre.htm"
        )

        # Construct today's date dynamically for the endpoint
        today = datetime.now()
        api_url = f"https://hydra.ugent.be/api/2.0/resto/menu/nl/{today.year}/{today.month}/{today.day}.json"
        print(f"today is: {today.year}-{today.month}-{today.day} Fetching data from: {api_url}")

        try:
            # Send GET request to the API
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors

            # Parse JSON response
            data = response.json()

            # Extract and print all items under the "meals" section
            if "meals" in data:
                for meal in data["meals"]:
                    # Safely access the 'name' and 'price' keys
                    name = meal.get("name", "Unnamed meal")
                    price = comma_float(meal.get("price", "€ 0.0").split(" ")[1])
                    products.add(Product(name=name, price=price))
            else:
                print("No 'meals' section found in the JSON response.")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as e:
            print(f"An error occurred: {e}")

        end_time = time.time()
        elapsed_time = end_time - start_time
        # Convert seconds to minutes and seconds
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        print(f"get_prices executed in {minutes} minute(s) and {seconds:.2f} second(s).")
        return products, locatie
