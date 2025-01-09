from core.property import Pos_x, Pos_y, Shape_x, Shape_y

class Event:
    pass

class SingleTargetEvent(Event):

    @staticmethod
    def check(previous, current, current_others) -> bool:
        raise NotImplementedError("Subclasses must implement this method.")

    @staticmethod
    def name():
        raise NotImplementedError("Subclasses must implement this method.")
    
    @staticmethod
    def id():
        raise NotImplementedError("Subclasses must implement this method.")

class Contact_With_Something_T(SingleTargetEvent):

    @staticmethod
    def check(previous, current, current_others) -> bool:
        hb1 = ((current.properties[Pos_x] - current.properties[Shape_x], current.properties[Pos_y] - current.properties[Shape_y]), (current.properties[Pos_x] + current.properties[Shape_x], current.properties[Pos_y] + current.properties[Shape_y]))
        for oe in current_others:
            hb2 = ((oe.properties[Pos_x] - oe.properties[Shape_x], oe.properties[Pos_y] - oe.properties[Shape_y]), (oe.properties[Pos_x] + oe.properties[Shape_x], oe.properties[Pos_y] + oe.properties[Shape_y]))
            if (hb1[0][1] - 1 == hb2[1][1] and hb1[0][0] < hb2[1][0] and hb1[1][0] > hb2[0][0]):
                return True
        return False

    @staticmethod
    def name(): return 'contact_top'
    
    @staticmethod
    def id(): return 1

class Contact_With_Something_B(SingleTargetEvent):

    @staticmethod
    def check(previous, current, current_others) -> bool:
        hb1 = ((current.properties[Pos_x] - current.properties[Shape_x], current.properties[Pos_y] - current.properties[Shape_y]), (current.properties[Pos_x] + current.properties[Shape_x], current.properties[Pos_y] + current.properties[Shape_y]))
        for oe in current_others:
            hb2 = ((oe.properties[Pos_x] - oe.properties[Shape_x], oe.properties[Pos_y] - oe.properties[Shape_y]), (oe.properties[Pos_x] + oe.properties[Shape_x], oe.properties[Pos_y] + oe.properties[Shape_y]))
            if (hb1[1][1] + 1 == hb2[0][1] and hb1[0][0] < hb2[1][0] and hb1[1][0] > hb2[0][0]):
                #print(f'contact between bottom side of {current}({hb1}) and {oe}({hb2})')
                return True
        return False

    @staticmethod
    def name(): return 'contact_bottom'
    
    @staticmethod
    def id(): return 2

class Contact_With_Something_L(SingleTargetEvent):

    @staticmethod
    def check(previous, current, current_others) -> bool:
        hb1 = ((current.properties[Pos_x] - current.properties[Shape_x], current.properties[Pos_y] - current.properties[Shape_y]), (current.properties[Pos_x] + current.properties[Shape_x], current.properties[Pos_y] + current.properties[Shape_y]))
        for oe in current_others:
            hb2 = ((oe.properties[Pos_x] - oe.properties[Shape_x], oe.properties[Pos_y] - oe.properties[Shape_y]), (oe.properties[Pos_x] + oe.properties[Shape_x], oe.properties[Pos_y] + oe.properties[Shape_y]))
            if (hb1[0][0] - 1 == hb2[1][0] and hb1[0][1] < hb2[1][1] and hb1[1][1] > hb2[0][1]):
                return True
        return False

    @staticmethod
    def name(): return 'contact_left'
    
    @staticmethod
    def id(): return 3

class Contact_With_Something_R(SingleTargetEvent):

    @staticmethod
    def check(previous, current, current_others) -> bool:
        hb1 = ((current.properties[Pos_x] - current.properties[Shape_x], current.properties[Pos_y] - current.properties[Shape_y]), (current.properties[Pos_x] + current.properties[Shape_x], current.properties[Pos_y] + current.properties[Shape_y]))
        for oe in current_others:
            hb2 = ((oe.properties[Pos_x] - oe.properties[Shape_x], oe.properties[Pos_y] - oe.properties[Shape_y]), (oe.properties[Pos_x] + oe.properties[Shape_x], oe.properties[Pos_y] + oe.properties[Shape_y]))
            if (hb1[1][0] + 1 == hb2[0][0] and hb1[0][1] < hb2[1][1] and hb1[1][1] > hb2[0][1]):
                return True
        return False

    @staticmethod
    def name(): return 'contact_right'
    
    @staticmethod
    def id(): return 4

event_pool = [Contact_With_Something_T, Contact_With_Something_B, Contact_With_Something_L, Contact_With_Something_R]
