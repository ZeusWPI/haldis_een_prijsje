class Product:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.price = 0.0
        self.choiceLists = []

    def __str__(self):
        output = ""
        display_name = self.name.lower().replace(
            " ", "_"
        ).replace(
            ".", "_dot_"
        ).replace(
            "+", "_plus_"
        ).replace(
            "€", "_euro_"
        )
        if self.description != "":
            output += f"dish {display_name}: {self.name} -- {self.description} € {self.price}\n"
        else:
            output += f"dish {display_name}: {self.name}  € {self.price}\n"
        for choiceList in self.choiceLists:
            output += f"{str(choiceList)}"
        return output

    def __repr__(self):
        return self.__str__()
