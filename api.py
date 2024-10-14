from flask import Flask, request, jsonify

from data_types.choice import ChoiceList, Choice, ChoiceType
from data_types.product import Product
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


def translate_products_to_text(products):
    product_list = list(products)
    product_list.sort(key=lambda product: product.name, reverse=False)
    output = ""
    for product in product_list:
        output += str(product)
    return output


def create_test_product():
    test_product = Product()
    test_product.name = "test_product_name"
    test_product.description = "test_product_description"
    test_product.price = 53.0

    choiceList = ChoiceList()
    choiceList.name = "size"
    choiceList.description = "Formaat"

    choice1 = Choice()
    choice1.name = "extra_small"
    choice1.price = 1.8

    choice2 = Choice()
    choice2.name = "small"
    choice2.price = 2

    choice3 = Choice()
    choice3.name = "medium"
    choice3.price = 2.5

    choice4 = Choice()
    choice4.name = "large"
    choice4.price = 3.3

    choiceList.choices = [choice1, choice2, choice3, choice4]
    test_product.choiceLists.append(choiceList)

    choiceList2 = ChoiceList()
    choiceList2.name = "verplichte_size"
    choiceList2.description = "Formaat"
    choiceList2.type = ChoiceType.MULTI
    choiceList2.choices = [choice1, choice2, choice3, choice4]
    test_product.choiceLists.append(choiceList2)

    return test_product


if __name__ == '__main__':
    app.run(debug=True)
