import re

from data_types.choice import ChoiceList, Choice, ChoiceType
from utils import only_keep_UTF_8_chars
from typing import List


class Product:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.price = 0.0
        self.choiceLists = []
        self.display_name = ""

    def __str__(self):
        output = ""
        self.name = only_keep_UTF_8_chars(self.name.replace("€", " euro "))
        self.display_name = only_keep_UTF_8_chars(self.name.lower().replace(
            " ", "_"
        ).replace(
            ".", "_dot_"
        ).replace(
            "+", "_plus_"
        ).replace(
            "€", "_euro_"
        ))

        self.name = re.sub(r'\s+', ' ', self.name).strip()
        if self.description != "":
            output += f"dish {self.display_name}: {self.name} -- {self.description} € {self.price}\n"
        else:
            output += f"dish {self.display_name}: {self.name}  € {self.price}\n"
        for choiceList in self.choiceLists:
            output += f"{str(choiceList)}"
        return output

    def __repr__(self):
        return self.__str__()

    def add_choiceList(self, choiceList):
        self.choiceLists.append(choiceList)

    def add_choiceList_indexed(self, index, choiceList):
        self.choiceLists.insert(index, choiceList)


def add_choiseList_to_product_by_name(products, choiceList, name_list: List[str]):
    for product in products:
        # print(product.name)
        if product.name in name_list:
            product.choiceLists.append(choiceList)


def translate_products_to_text(products):
    product_list = list(products)
    product_list.sort(key=lambda product: product.name, reverse=False)
    output = ""
    for product in product_list:
        output += str(product)
    return output


def merge_products(all_products, merged_products_names, name, option_names):
    prices = [float(product.price) for product in all_products if product.name in merged_products_names]
    prices.sort()
    product = [product for product in all_products if product.name == merged_products_names[0]][0]
    all_products = [product for product in all_products if product.name not in merged_products_names[1:]]

    merge_keuze_list = ChoiceList(name="groote", description="Welk groote?")

    choises = [Choice(choice_name) for choice_name in option_names]

    for i, choice in enumerate(choises):
        choice.price = prices[i]-prices[0]

    merge_keuze_list.choices = choises

    product.name = name
    product.add_choiceList_indexed(0, merge_keuze_list)
    return all_products


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
