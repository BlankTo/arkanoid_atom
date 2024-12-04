class SingleTargetEvent:
    def check(self, element, other_elements) -> bool:
        raise NotImplementedError("Subclasses must implement this method.")
    def __repr__(self):
        raise NotImplementedError("Subclasses must implement this method.")

class Contact_With_Something_T(SingleTargetEvent):
    def check(self, element, other_elements) -> bool:
        hb1 = element.properties['hitbox']
        for oe in other_elements:
            hb2 = oe.properties['hitbox']
            if (hb1[1][1] + 1 == hb2[0][1] and hb1[0][0] < hb2[1][0] and hb1[1][0] > hb2[0][0]):
                return True
        return False
    def __repr__(self):
        return "contact_top"

class Contact_With_Something_B(SingleTargetEvent):
    def check(self, element, other_elements) -> bool:
        hb1 = element.properties['hitbox']
        for oe in other_elements:
            hb2 = oe.properties['hitbox']
            if (hb1[0][1] - 1 == hb2[1][1] and hb1[0][0] < hb2[1][0] and hb1[1][0] > hb2[0][0]):
                return True
        return False
    def __repr__(self):
        return "contact_bottom"

class Contact_With_Something_L(SingleTargetEvent):
    def check(self, element, other_elements) -> bool:
        hb1 = element.properties['hitbox']
        for oe in other_elements:
            hb2 = oe.properties['hitbox']
            if (hb1[0][0] - 1 == hb2[1][0] and hb1[0][1] < hb2[1][1] and hb1[1][1] > hb2[0][1]):
                return True
        return False
    def __repr__(self):
        return "contact_left"

class Contact_With_Something_R(SingleTargetEvent):
    def check(self, element, other_elements) -> bool:
        hb1 = element.properties['hitbox']
        for oe in other_elements:
            hb2 = oe.properties['hitbox']
            if (hb1[1][0] + 1 == hb2[0][0] and hb1[0][1] < hb2[1][1] and hb1[1][1] > hb2[0][1]):
                return True
        return False
    def __repr__(self):
        return "contact_right"
