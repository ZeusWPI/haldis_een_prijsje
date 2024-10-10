import requests
from bs4 import BeautifulSoup
from data_types.product import Product
from scrapers.scraper import Scraper


class MetropolScraper(Scraper):

    @staticmethod
    def get_prices() -> set[Product]:

        base_url = "https://snackmetropol.be/Menu/Menu/ProductsByCategory?categoryId="
        # URL of the webpage you want to extract HTML from
        extra_url_s = [
            "25472&_=1728579094939",
            "25473&_=1728579094940",
            "25474&_=1728580943523",
            "25475&_=1728580943524",
            "25476&_=1728580943525",
            "25478&_=1728580943526",
            "25480&_=1728580943529",
            "25481&_=1728580943530",
            "25755&_=1728580943531",
            "34984&_=1728580943532",
            "42886&_=1728580943533"
        ]

        products = set()

        for link in extra_url_s:
            # Send a GET request to the webpage
            full_link = base_url + link
            # print(full_link)
            response = requests.get(full_link)

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # # Get the entire HTML content
            # html_content = soup.prettify()
            #
            # # Print or save the HTML content
            # print(html_content)

            # Find all divs with class 'product-prices span3'
            divs = soup.find_all('div', class_='product-section row-fluid')

            # Print the found divs
            for div in divs:
                # print(div.prettify())
                product = Product()
                # Find and print the 'p' tag with class 'product-name'
                product_name = div.find('p', class_='product-name')
                if product_name:
                    product.update_name(product_name.get_text().strip())

                # Find and print the 'span' tag with class 'product-price'
                product_price = div.find('span', class_='product-price')
                if product_price:
                    product.update_price(product_price.get_text().strip().split(" ")[-1].replace(',', '.'))
                # print(product)
                products.add(product)

        return products
