import random

from core.object import Object, Rule

class Individual:

    def __init__(self, id, object_id_generator, objects= None):

        self.id = id
        self.object_id_generator = object_id_generator
        if objects is not None:
            self.objects = [Object(id= self.object_id_generator(), rules= [rule for rule in obj.rules]) for obj in objects]
        self.fitness = None

    def initialize(self, event_pool, property_pool, coefficient_pool) -> 'Individual':

        n_obj = random.randint(1, 3)
        self.objects = [Object(id= self.object_id_generator()).initialize(event_pool, property_pool, coefficient_pool) for _ in range(n_obj)]
        return self