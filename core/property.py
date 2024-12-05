

class Property:

    @staticmethod
    def compute(elem0, elem1, other_elements1):
        raise NotImplementedError('subclass have to implement "compute" function')
    
    @staticmethod
    def effects(prop_value, properties):
        raise NotImplementedError('subclass have to implement "effect" function')

    @staticmethod
    def name():
        raise NotImplementedError('subclass have to implement "name" function')

class Speed_x(Property):

    @staticmethod
    def compute(elem0, elem1, other_elements1):
        return elem1.properties['pos_x'] - elem0.properties['pos_x']
    
    @staticmethod
    def effects(prop_value, properties):
        return {'pos_x': prop_value, 'hitbox_tl_x': prop_value, 'hitbox_br_x': prop_value}
    
    @staticmethod
    def name():
        return 'vx'

class Speed_y(Property):

    @staticmethod
    def compute(elem0, elem1, other_elements1):
        return elem1.properties['pos_y'] - elem0.properties['pos_y']
    
    @staticmethod
    def effects(prop_value, properties):
        return {'pos_y': prop_value, 'hitbox_tl_y': prop_value, 'hitbox_br_y': prop_value}
    
    @staticmethod
    def name():
        return 'vy'