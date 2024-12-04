class Element:
    def __init__(self, id, description, properties):
        self.id = id
        self.description = description # debug purpose
        self.properties = properties  # for now {"pos": (x, y), "hitbox": ((xmin, ymin), (xmax, ymax))}

    def __repr__(self):
        return f"Element({self.description}, {self.properties})"
