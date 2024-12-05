import random

from .rule import Rule

class Object:
    def __init__(self, id, rules= None):
        self.id = id
        if rules is not None: self.rules = [Rule(events= [event for event in rule.events], property_class= rule.property_class, coefficient = rule.coefficient) for rule in rules]
        else: self.rules = None

    def initialize(self, event_pool, property_pool, coefficient_pool) -> 'Object':

        n_rules = random.randint(0, 3)
        self.rules = [Rule().initialize(event_pool, property_pool, coefficient_pool) for _ in range(n_rules)]

        return self
    
    def get_properties_class(self):
        return [rule.property_class for rule in self.rules]

    def __repr__(self):
        ss = f"Object_{self.id} - Rules:"
        for rule in self.rules: ss += f"\n >> {rule}"
        return ss