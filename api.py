from flask import Flask, request, jsonify
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
        metropol_products = MetropolScraper.get_prices()
        print(metropol_products)
        return jsonify([{"name": product.name, "price": product.price} for product in metropol_products])

    return jsonify({"error": "Restaurant not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
