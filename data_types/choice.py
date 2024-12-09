from enum import Enum

from utils import only_keep_UTF_8_chars


class ChoiceType(Enum):
    SINGLE = 1
    MULTI = 2


class Choice:
    def __init__(self, name: str = "", price: float = 0.0):
        self.type: ChoiceType = ChoiceType.SINGLE
        self.name: str = name
        self.price: float = price

    def __str__(self):
        self.name = only_keep_UTF_8_chars(self.name.replace("€", " euro "))
        display_name = only_keep_UTF_8_chars(self.name.lower().replace(
            " ", "_"
        ).replace(
            ".", "_dot_"
        ).replace(
            "+", "_plus_"
        ).replace(
            "€", "_euro_"
        ))
        return f"{display_name}: {self.name}  € {self.price}"

    def __repr__(self):
        return self.__str__()


class ChoiceList:
    def __init__(self, name: str = "", description: str = "", type: ChoiceType = ChoiceType.SINGLE):
        self.type: ChoiceType = type
        self.choices = []
        self.name: str = name
        self.description: str = description

    def update_name(self, new_name: str):
        temp = ChoiceList(name=new_name)
        temp.choices = self.choices
        return temp

    def __str__(self):
        output = ""
        if self.type == ChoiceType.SINGLE:
            output += f"\tsingle_choice {self.name}: {self.description}\n"
        elif self.type == ChoiceType.MULTI:
            output += f"\tmulti_choice {self.name}: {self.description}\n"

        for choice in self.choices:
            output += f"\t\t{str(choice)}\n"

        return output

    def __repr__(self):
        return self.__str__()

    def add_choice(self, choice: Choice):
        self.choices.append(choice)
