import random


class Rule:
    def __init__(self, events= None, property_class= None, coefficient= None):
        self.events = events  # List of events triggering this rule
        self.property_class = property_class  # Property to which this rule applies (e.g., "vx")
        self.coefficient = coefficient  # Fixed rule-specific coefficient (a)

    def initialize(self, event_pool, property_pool, coefficient_pool) -> 'Rule':
        
        n_triggers = random.randint(1, len(event_pool))
        self.events = random.sample(event_pool, n_triggers)

        self.property_class = random.choice(property_pool)
        
        self.coefficient = random.choice(coefficient_pool)

        return self

    def __repr__(self):
        return f"({self.events}) -> {self.property_class.name()}1 = {self.property_class.name()}0 + ({self.coefficient}) * k"