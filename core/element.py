from core.property import Pos_x, Pos_y

class Element:
    def __init__(self, id, description, properties):
        self.id = id
        self.description = description
        self.properties = properties

    def __repr__(self):
        return f"Element({self.description}, {(self.properties[Pos_x], self.properties[Pos_y])})"
