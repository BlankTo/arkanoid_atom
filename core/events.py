class SingleTargetEvent:
    def check(self, element0, element1, other_elements1) -> bool:
        raise NotImplementedError("Subclasses must implement this method.")
    def __repr__(self):
        raise NotImplementedError("Subclasses must implement this method.")

class Contact_With_Something_T(SingleTargetEvent):
    def check(self, element0, element1, other_elements1) -> bool:
        hb1 = ((element1.properties['hitbox_tl_x'], element1.properties['hitbox_tl_y']), (element1.properties['hitbox_br_x'], element1.properties['hitbox_br_y']))
        for oe in other_elements1:
            hb2 = ((oe.properties['hitbox_tl_x'], oe.properties['hitbox_tl_y']), (oe.properties['hitbox_br_x'], oe.properties['hitbox_br_y']))
            if (hb1[1][1] + 1 == hb2[0][1] and hb1[0][0] < hb2[1][0] and hb1[1][0] > hb2[0][0]):
                return True
        return False
    def __repr__(self):
        return "contact_top"

class Contact_With_Something_B(SingleTargetEvent):
    def check(self, element0, element1, other_elements1) -> bool:
        hb1 = ((element1.properties['hitbox_tl_x'], element1.properties['hitbox_tl_y']), (element1.properties['hitbox_br_x'], element1.properties['hitbox_br_y']))
        for oe in other_elements1:
            hb2 = ((oe.properties['hitbox_tl_x'], oe.properties['hitbox_tl_y']), (oe.properties['hitbox_br_x'], oe.properties['hitbox_br_y']))
            if (hb1[0][1] - 1 == hb2[1][1] and hb1[0][0] < hb2[1][0] and hb1[1][0] > hb2[0][0]):
                return True
        return False
    def __repr__(self):
        return "contact_bottom"

class Contact_With_Something_L(SingleTargetEvent):
    def check(self, element0, element1, other_elements1) -> bool:
        hb1 = ((element1.properties['hitbox_tl_x'], element1.properties['hitbox_tl_y']), (element1.properties['hitbox_br_x'], element1.properties['hitbox_br_y']))
        for oe in other_elements1:
            hb2 = ((oe.properties['hitbox_tl_x'], oe.properties['hitbox_tl_y']), (oe.properties['hitbox_br_x'], oe.properties['hitbox_br_y']))
            if (hb1[0][0] - 1 == hb2[1][0] and hb1[0][1] < hb2[1][1] and hb1[1][1] > hb2[0][1]):
                return True
        return False
    def __repr__(self):
        return "contact_left"

class Contact_With_Something_R(SingleTargetEvent):
    def check(self, element0, element1, other_elements1) -> bool:
        hb1 = ((element1.properties['hitbox_tl_x'], element1.properties['hitbox_tl_y']), (element1.properties['hitbox_br_x'], element1.properties['hitbox_br_y']))
        for oe in other_elements1:
            hb2 = ((oe.properties['hitbox_tl_x'], oe.properties['hitbox_tl_y']), (oe.properties['hitbox_br_x'], oe.properties['hitbox_br_y']))
            if (hb1[1][0] + 1 == hb2[0][0] and hb1[0][1] < hb2[1][1] and hb1[1][1] > hb2[0][1]):
                return True
        return False
    def __repr__(self):
        return "contact_right"
