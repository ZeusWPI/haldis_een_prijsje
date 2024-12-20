import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from data_types.product import translate_products_to_text
from scrapers.bicyclette_scraper import BicycletteScraper
from scrapers.bocca_ovp_scraper import BoccaOvpScraper
from scrapers.pizza_donna_scraper import PizzaDonnaScraper
from scrapers.s5_scraper import S5Scraper
from scrapers.simpizza_scraper import SimpizzaScraper
from scrapers.snackmetropol_scraper import MetropolScraper


def run_metropol():
    metropol_products, metropol_location = MetropolScraper.get_prices()
    with open("hlds_files/metropol.hlds", "w", encoding="utf-8") as file:
        file.write(str(metropol_location) + "\n")
        file.write(translate_products_to_text(metropol_products))
    print("metropol done", flush=True)
    return len(metropol_products)


def run_bicyclette():
    bicyclette_products, bicyclette_location = BicycletteScraper.get_prices()
    with open("hlds_files/bicyclette.hlds", "w", encoding="utf-8") as file:
        file.write(str(bicyclette_location) + "\n")
        file.write(translate_products_to_text(bicyclette_products))
    print("bicyclette done", flush=True)
    return len(bicyclette_products)


def run_simpizza():
    simpizza_products, simpizza_location = SimpizzaScraper.get_prices()
    with open("hlds_files/simpizza.hlds", "w", encoding="utf-8") as file:
        file.write(str(simpizza_location) + "\n")
        file.write(translate_products_to_text(simpizza_products))
    print("simpizza done", flush=True)
    return len(simpizza_products)


def run_pizza_donna():
    pizza_donna_products, pizza_donna_location = PizzaDonnaScraper.get_prices()
    with open("hlds_files/pizza_donna.hlds", "w", encoding="utf-8") as file:
        file.write(str(pizza_donna_location) + "\n")
        file.write(translate_products_to_text(pizza_donna_products))
    print("pizza_donna done", flush=True)
    return len(pizza_donna_products)


def run_bocca_ovp():
    bocca_ovp_products, bocca_ovp_location = BoccaOvpScraper.get_prices()
    with open("hlds_files/bocca_ovp.hlds", "w", encoding="utf-8") as file:
        file.write(str(bocca_ovp_location) + "\n")
        file.write(translate_products_to_text(bocca_ovp_products))
    print("bocca_ovp done", flush=True)
    return len(bocca_ovp_products)


def run_s5():
    s5_products, s5_location = S5Scraper.get_prices()
    with open("hlds_files/s5.hlds", "w", encoding="utf-8") as file:
        file.write(str(s5_location) + "\n")
        file.write(translate_products_to_text(s5_products))
    print("s5 done")
    return len(s5_products)


def parse_arguments():
    """
    Parse command-line arguments for controlling the script.
    """
    parser = argparse.ArgumentParser(description="Run restaurant scrapers and save data.")
    parser.add_argument(
        "--run-everything",
        action="store_true",
        help="Run scrapers for all restaurants.",
    )
    parser.add_argument(
        "--use-parallelism",
        action="store_true",
        help="Enable parallel execution of scrapers.",
    )
    parser.add_argument(
        "--restaurant-name",
        type=str,
        nargs="*",  # Accepts a list of restaurant names
        help="Specify the restaurants to scrape data for (space-separated list).",
    )
    return parser.parse_args()


def run_scrapers(
        run_everything: bool = False,
        use_parallelism: bool = False,
        restaurant_names=None
):
    if restaurant_names is None:
        restaurant_names = ["pizza_donna"]
    start_time = time.time()
    # Default values
    # Parse command-line arguments
    # args = parse_arguments()

    # Use arguments if provided, otherwise fall back to defaults
    # run_everything = args.run_everything if args.run_everything else default_run_everything
    # use_parallelism = args.use_parallelism if args.use_parallelism else default_use_parallelism
    # restaurant_names = args.restaurant_name if args.restaurant_name else default_restaurant_names

    tasks = []
    if run_everything or "metropol" in [name.lower() for name in restaurant_names]:
        tasks.append(run_metropol)
    if run_everything or "bicyclette" in [name.lower() for name in restaurant_names]:
        tasks.append(run_bicyclette)
    if run_everything or "simpizza" in [name.lower() for name in restaurant_names]:
        tasks.append(run_simpizza)
    if run_everything or "bocca_ovp" in [name.lower() for name in restaurant_names]:
        tasks.append(run_bocca_ovp)
    if run_everything or "pizza_donna" in [name.lower() for name in restaurant_names]:
        tasks.append(run_pizza_donna)
    if run_everything or "s5" in [name.lower() for name in restaurant_names]:
        tasks.append(run_s5)

    # print(f"Restaurants: {args.restaurant_name},evaluates to {"everything because run_everything is selected" if run_everything else restaurant_names}")
    # print(f"Parallel: {args.use_parallelism},evaluates to {use_parallelism}")
    # print(f"Run everything: {args.run_everything},evaluates to {run_everything}")

    total_products = 0
    if use_parallelism:
        # Run tasks in parallel
        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda func: func(), tasks)
            total_products = sum(results)
    else:
        # Run tasks sequentially
        for task in tasks:
            total_products += task()

    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = elapsed_time % 60
    print(f"main executed in {minutes} minute(s) and {seconds:.2f} second(s).", flush=True)
    return {
        "restaurant_names": restaurant_names,
        "total_products_scraped": total_products,
    }


if __name__ == "__main__":
    # Default values
    default_run_everything: bool = False
    default_use_parallelism: bool = False
    default_restaurant_names = ["bocca_ovp"]

    # Parse command-line arguments
    args = parse_arguments()

    # Use arguments if provided, otherwise fall back to defaults
    run_everything = args.run_everything if args.run_everything else default_run_everything
    use_parallelism = args.use_parallelism if args.use_parallelism else default_use_parallelism
    restaurant_names = args.restaurant_name if args.restaurant_name else default_restaurant_names

    print(
        f"Restaurants: {args.restaurant_name},evaluates to {"everything because run_everything is selected" if run_everything else restaurant_names}")
    print(f"Parallel: {args.use_parallelism},evaluates to {use_parallelism}")
    print(f"Run everything: {args.run_everything},evaluates to {run_everything}")

    run_scrapers(run_everything=run_everything, use_parallelism=use_parallelism, restaurant_names=restaurant_names)
