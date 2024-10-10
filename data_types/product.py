class Product:
    def __init__(self):
        self.name = ""
        self.price = 0.0

    def update_name(self, name):
        self.name = name

    def update_price(self, price):
        self.price = price

    def get_name(self):
        return self.name
    def get_price(self):
        return self.price

    def __str__(self):
        return self.name + " has price " + str(self.price)

    def __repr__(self):
        return self.__str__()