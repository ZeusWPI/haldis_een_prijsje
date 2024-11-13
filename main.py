from scrapers.snackmetropol_scraper import MetropolScraper
from utils import create_test_product, translate_products_to_text

metropol_products = MetropolScraper.get_prices()

if __name__ == '__main__':
    run_everything = True
    restaurant_name = "metropol"
    if restaurant_name.lower() == "metropol" or run_everything:
        metropol_products, metropol_location = MetropolScraper.get_prices()
        test_product = create_test_product()
        # Open a file and write the result to it
        with open("hlds_files/metropol.hlds", "w") as file:
            file.write(str(metropol_location) + "\n")
            file.write(translate_products_to_text(metropol_products))

# print(metropol_products)
# print(len(metropol_products))
