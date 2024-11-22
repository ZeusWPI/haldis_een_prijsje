from flask import Flask, request, jsonify

from data_types.product import translate_products_to_text, create_test_product
from scrapers.snackmetropol_scraper import MetropolScraper

app = Flask(__name__)

@app.route('/api/products', methods=['GET'])
def get_products():
    restaurant_name = request.args.get('restaurant')
    if not restaurant_name:
        return jsonify({"error": "Restaurant name is required"}), 400

    # Define base URL and extra parts based on the restaurant name
    # For example purposes, you can create a mapping or use conditions
    if restaurant_name.lower() == "metropol":
        metropol_products, metropol_location = MetropolScraper.get_prices()
        test_product = create_test_product()
        # print(str(test_product))
        # metropol_products.add(test_product)
        # print(metropol_products)
        # Open a file and write the result to it
        with open("hlds_files/metropol.hlds", "w") as file:
            file.write(str(metropol_location) + "\n")
            file.write(translate_products_to_text(metropol_products))
        return jsonify(
            [
                {
                    "name": product.name,
                    "description": product.description,
                    "price": product.price
                } for product in metropol_products
            ]
        )

    return jsonify({"error": "Restaurant not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
