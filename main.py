from scrapers.snackmetropol_scraper import MetropolScraper

metropol_products = MetropolScraper.get_prices()

print(metropol_products)
print(len(metropol_products))
