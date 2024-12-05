

class Property:

    @staticmethod
    def compute(elem0, elem1, other_elements1):
        raise NotImplementedError('subclass have to implement "compute" function')

    @staticmethod
    def name():
        raise NotImplementedError('subclass have to implement "name" function')

class Speed_x(Property):

    @staticmethod
    def compute(elem0, elem1, other_elements1):
        return elem1.properties['pos'][0] - elem0.properties['pos'][0]
    
    @staticmethod
    def name():
        return 'vx'

class Speed_y(Property):

    @staticmethod
    def compute(elem0, elem1, other_elements1):
        return elem1.properties['pos'][1] - elem0.properties['pos'][1]
    
    @staticmethod
    def name():
        return 'vy'