import random

class Rule:
    def __init__(self, events= None, property_name= None, coefficient= None):
        self.events = events  # List of events triggering this rule
        self.property_name = property_name  # Property to which this rule applies (e.g., "vx")
        self.coefficient = coefficient  # Fixed rule-specific coefficient (a)

    def initialize(self, event_pool, property_pool, coefficient_pool) -> 'Rule':
        
        n_triggers = random.randint(1, len(event_pool))
        self.events = random.sample(event_pool, n_triggers)

        self.property_name = random.choice(property_pool)
        
        self.coefficient = random.choice(coefficient_pool)

        return self

    def __repr__(self):
        return f"({self.events}) -> {self.property_name}1 = {self.property_name}0 + ({self.coefficient}) * k"

class Object:
    def __init__(self, id, rules= None):
        self.id = id
        if rules is not None: self.rules = [Rule(events= [event for event in rule.events], property_name= rule.property_name, coefficient = rule.coefficient) for rule in rules]
        else: self.rules = None

    def initialize(self, event_pool, property_pool, coefficient_pool) -> 'Object':

        n_rules = random.randint(0, 3)
        self.rules = [Rule().initialize(event_pool, property_pool, coefficient_pool) for _ in range(n_rules)]

        return self

    def __repr__(self):
        ss = f"Object_{self.id} - Rules:"
        for rule in self.rules: ss += f"\n >> {rule}"
        return ss

#TODO: realization class here or in its own file