

class Property:

    @staticmethod
    def compute(previous, current, current_others):
        raise NotImplementedError()

    @staticmethod
    def effects(property_values):
        raise NotImplementedError()
    
    @staticmethod
    def get_dependant_properties():
        raise NotImplementedError()
    
    @staticmethod
    def name():
        raise NotImplementedError()

class Pos_x(Property):

    @staticmethod
    def compute(previous, current, current_others): return current.properties[Pos_x]
    
    @staticmethod
    def effects(properties): return {}
    
    @staticmethod
    def get_dependant_properties(): return []
    
    @staticmethod
    def name(): return 'pos_x'

class Pos_y(Property):

    @staticmethod
    def compute(previous, current, current_others): return current.properties[Pos_y]
    
    @staticmethod
    def effects(properties): return {}
    
    @staticmethod
    def get_dependant_properties(): return []
    
    @staticmethod
    def name(): return 'pos_y'

class Hitbox_tl_x(Property):

    @staticmethod
    def compute(previous, current, current_others): return current.properties[Hitbox_tl_x]
    
    @staticmethod
    def effects(properties): return {}
    
    @staticmethod
    def get_dependant_properties(): return []
    
    @staticmethod
    def name(): return 'hitbox_tl_x'

class Hitbox_tl_y(Property):

    @staticmethod
    def compute(previous, current, current_others): return current.properties[Hitbox_tl_y]
    
    @staticmethod
    def effects(properties): return {}
    
    @staticmethod
    def get_dependant_properties(): return []
    
    @staticmethod
    def name(): return 'hitbox_tl_y'

class Hitbox_br_x(Property):

    @staticmethod
    def compute(previous, current, current_others): return current.properties[Hitbox_br_x]
    
    @staticmethod
    def effects(properties): return {}
    
    @staticmethod
    def get_dependant_properties(): return []
    
    @staticmethod
    def name(): return 'hitbox_br_x'

class Hitbox_br_y(Property):

    @staticmethod
    def compute(previous, current, current_others): return current.properties[Hitbox_br_y]
    
    @staticmethod
    def effects(properties): return {}
    
    @staticmethod
    def get_dependant_properties(): return []
    
    @staticmethod
    def name(): return 'hitbox_br_y'

class Speed_x(Property):

    @staticmethod
    def compute(previous, current, current_others): return current.properties[Pos_x] - previous.properties[Pos_x]
    
    @staticmethod
    def effects(properties):
        return {Pos_x: properties[Speed_x], Hitbox_tl_x: properties[Speed_x], Hitbox_br_x: properties[Speed_x]}
    
    @staticmethod
    def get_dependant_properties(): return [Pos_x, Hitbox_tl_x, Hitbox_br_x]
    
    @staticmethod
    def name(): return 'vx'

class Speed_y(Property):

    @staticmethod
    def compute(previous, current, current_others): return current.properties[Pos_y] - previous.properties[Pos_y]
    
    @staticmethod
    def effects(properties):
        return {Pos_y: properties[Speed_y], Hitbox_tl_y: properties[Speed_y], Hitbox_br_y: properties[Speed_y]}
    
    @staticmethod
    def get_dependant_properties(): return [Pos_y, Hitbox_tl_y, Hitbox_br_y]
    
    @staticmethod
    def name(): return 'vy'