from data_types.product import translate_products_to_text
from scrapers.bicyclette_scraper import BicycletteScraper
from scrapers.simpizza_scraper import SimpizzaScraper
from scrapers.snackmetropol_scraper import MetropolScraper

metropol_products = MetropolScraper.get_prices()

if __name__ == '__main__':
    run_everything = False
    restaurant_name = "simpizza"
    if restaurant_name.lower() == "metropol" or run_everything:
        metropol_products, metropol_location = MetropolScraper.get_prices()
        # Open a file and write the result to it
        with open("hlds_files/metropol.hlds", "w", encoding="utf-8") as file:
            file.write(str(metropol_location) + "\n")
            file.write(translate_products_to_text(metropol_products))
        print("metropol done")

    if restaurant_name.lower() == "bicyclette" or run_everything:
        bicyclette_products, bicyclette_location = BicycletteScraper.get_prices()
        # Open a file and write the result to it
        with open("hlds_files/bicyclette.hlds", "w", encoding="utf-8") as file:
            file.write(str(bicyclette_location) + "\n")
            file.write(translate_products_to_text(bicyclette_products))
        print("bicyclette done")

    if restaurant_name.lower() == "simpizza" or run_everything:
        simpizza_products, simpizza_location = SimpizzaScraper.get_prices()
        # Open a file and write the result to it
        with open("hlds_files/simpizza.hlds", "w", encoding="utf-8") as file:
            file.write(str(simpizza_location) + "\n")
            file.write(translate_products_to_text(simpizza_products))
        print("simpizza done")

# print(metropol_products)
# print(len(metropol_products))
