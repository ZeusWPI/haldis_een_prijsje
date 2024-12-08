import time

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By

from data_types.choice import Choice, ChoiceList
from data_types.location import Location
from data_types.product import Product
from scrapers.scraper import Scraper

from seleniumbase import SB

from utils import download_pdf, parse_pdf, get_page_dimensions


# http://www.bocca.be/menus/take-away.html
class BoccaOvpScraper(Scraper):

    @staticmethod
    def get_prices() -> (set[Product], Location):
        start_time = time.time()
        products = set()
        locatie = Location(
            "bocca: Bocca",
            "https://www.openstreetmap.org/node/1462321981#map=19/51.038423/3.726819",
            "Citadellaan 4, 9000 Ghent",
            "+32 (0)9 245 37 99",
            "http://www.bocca.be/"
        )
        # Define the URL and file path
        pdf_url = "http://www.bocca.be/documents/BOCCA_TAKEAWAY.pdf"
        local_file_path = "bocca_takeaway.pdf"

        # Download and parse the PDF
        download_pdf(pdf_url, local_file_path)
        width, height = get_page_dimensions(local_file_path, page_number=1)
        x_lim = 200
        top_y_lim = 200
        bottom_y_lim = 350
        sauce_to_go = parse_pdf(local_file_path, coords=(0, top_y_lim, x_lim, height - bottom_y_lim))

        # Split text by lines, then process each line
        lines = sauce_to_go.strip().split("\n")
        parts = lines[0].split(" ")
        size_small = parts[len(parts) - 2].strip()
        size_large = parts[len(parts) - 1].strip()
        keep_text = ""
        for line in lines[1:]:
            # Split the line by spaces, separating the name and sizes/prices
            parts = line.split(" ")
            name = " ".join(parts[:-2])  # Everything except the last two parts
            if keep_text:
                name = keep_text + " " + name
                keep_text = ""
            name = "SAUCE TO GO " + name

            try:
                keuze_lijst = ChoiceList(name="what size?")
                # Check if the last part is a size/price and collect it
                prize_small = float(parts[len(parts) - 2].replace(",", "."))
                prize_large = float(parts[len(parts) - 1].replace(",", "."))
                keuze_lijst.add_choice(Choice(name=size_small, price=0.0))
                keuze_lijst.add_choice(Choice(name=size_large, price=prize_large-prize_small))
            except ValueError:
                keep_text = " ".join(parts)
                continue

            # Create the product object
            product = Product(name=name, price=prize_small)
            product.add_choiceList(keuze_lijst)
            products.add(product)

        end_time = time.time()
        elapsed_time = end_time - start_time
        # Convert seconds to minutes and seconds
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        print(f"get_prices executed in {minutes} minute(s) and {seconds:.2f} second(s).")
        return products, locatie
