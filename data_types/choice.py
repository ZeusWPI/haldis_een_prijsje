from enum import Enum


class ChoiceType(Enum):
    SINGLE = 1
    MULTI = 2


class Choice:
    def __init__(self):
        self.type: ChoiceType = ChoiceType.SINGLE
        self.name: str = ""
        self.price: float = 0.0

    def __str__(self):
        display_name = self.name.lower().replace(
            " ", "_"
        ).replace(
            ".", "_dot_"
        ).replace(
            "+", "_plus_"
        ).replace(
            "€", "_euro_"
        )
        return f"{display_name}: {self.name}  € {self.price}"

    def __repr__(self):
        return self.__str__()


class ChoiceList:
    def __init__(self):
        self.type: ChoiceType = ChoiceType.SINGLE
        self.choices = []
        self.name: str = ""
        self.description: str = ""

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
