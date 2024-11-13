import re

import requests
from requests.exceptions import ConnectionError

from data_types.choice import ChoiceList, Choice, ChoiceType
from data_types.product import Product


def only_keep_UTF_8_chars(text):
    output = ''.join([char for char in text if char.encode('utf-8', 'ignore')])
    output = re.sub(r'[^\x00-\x7F]+', '', output)
    return output


def safe_get(link: str):
    try:
        return requests.get(link)
    except ConnectionError as e:
        print("error happend: " + str(e))
        # exit(1)
        return ""


def translate_products_to_text(products):
    product_list = list(products)
    product_list.sort(key=lambda product: product.name, reverse=False)
    output = ""
    for product in product_list:
        output += str(product)
    return only_keep_UTF_8_chars(output)


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
