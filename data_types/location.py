class Location:

    def __init__(self, name, osm, address, telephone, website):
        self.name = name
        self.osm = osm
        self.address = address
        self.telephone = telephone
        self.website = website

    def __str__(self):
        output = "==========================\n"
        output += self.name + "\n"
        if self.osm != "":
            output += "\tosm     " + self.osm + "\n"
        if self.telephone != "":
            output += "\tphone   " + self.telephone + "\n"
        if self.address != "":
            output += "\taddress " + self.address + "\n"
        if self.website != "":
            output += "\twebsite " + self.website + "\n"
        output += "==========================\n"
        return output

    def __repr__(self):
        return self.__str__()
