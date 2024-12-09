import time
from concurrent.futures import ThreadPoolExecutor
from data_types.product import translate_products_to_text
from scrapers.bicyclette_scraper import BicycletteScraper
from scrapers.bocca_ovp_scraper import BoccaOvpScraper
from scrapers.simpizza_scraper import SimpizzaScraper
from scrapers.snackmetropol_scraper import MetropolScraper


def run_metropol():
    metropol_products, metropol_location = MetropolScraper.get_prices()
    with open("hlds_files/metropol.hlds", "w", encoding="utf-8") as file:
        file.write(str(metropol_location) + "\n")
        file.write(translate_products_to_text(metropol_products))
    print("metropol done")


def run_bicyclette():
    bicyclette_products, bicyclette_location = BicycletteScraper.get_prices()
    with open("hlds_files/bicyclette.hlds", "w", encoding="utf-8") as file:
        file.write(str(bicyclette_location) + "\n")
        file.write(translate_products_to_text(bicyclette_products))
    print("bicyclette done")


def run_simpizza():
    simpizza_products, simpizza_location = SimpizzaScraper.get_prices()
    with open("hlds_files/simpizza.hlds", "w", encoding="utf-8") as file:
        file.write(str(simpizza_location) + "\n")
        file.write(translate_products_to_text(simpizza_products))
    print("simpizza done")


def run_bocca_ovp():
    bocca_ovp_products, bocca_ovp_location = BoccaOvpScraper.get_prices()
    with open("hlds_files/bocca_ovp.hlds", "w", encoding="utf-8") as file:
        file.write(str(bocca_ovp_location) + "\n")
        file.write(translate_products_to_text(bocca_ovp_products))
    print("bocca_ovp done")


if __name__ == '__main__':
    start_time = time.time()
    run_everything = False
    use_parallelism = False  # Set this to False to disable parallelism
    restaurant_name = "bocca_ovp"

    tasks = []
    if restaurant_name.lower() == "metropol" or run_everything:
        tasks.append(run_metropol)
    if restaurant_name.lower() == "bicyclette" or run_everything:
        tasks.append(run_bicyclette)
    if restaurant_name.lower() == "simpizza" or run_everything:
        tasks.append(run_simpizza)
    if restaurant_name.lower() == "bocca_ovp" or run_everything:
        tasks.append(run_bocca_ovp)

    if use_parallelism:
        # Run tasks in parallel
        with ThreadPoolExecutor() as executor:
            executor.map(lambda func: func(), tasks)
    else:
        # Run tasks sequentially
        for task in tasks:
            task()

    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = elapsed_time % 60
    print(f"main executed in {minutes} minute(s) and {seconds:.2f} second(s).")
