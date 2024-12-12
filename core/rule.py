import random


class Rule:
    def __init__(self, events= None, property_class= None, coefficient= None):
        self.events = events  # List of events triggering this rule
        self.property_class = property_class  # Property to which this rule applies (e.g., "vx")
        self.coefficient = coefficient  # Fixed rule-specific coefficient (a)

    def initialize(self, event_pool, property_pool, coefficient_pool) -> 'Rule':
        
        #self.events = random.sample(event_pool, random.randint(1, len(event_pool)))
        self.events = [random.choice(event_pool)]

        self.property_class = random.choice(property_pool)
        
        self.coefficient = random.choice(coefficient_pool)

        return self
    
    def effects(self, current_events):

        triggered = True

        for event in self.events:
            if event not in current_events:
                triggered = False
                break
        
        if triggered: return True, {self.property_class: self.coefficient}
        else: return False, {}
    
    def compute_effect(self):
        return {self.property_class: self.coefficient}
    
    def add_trigger(self, event_pool):

        self.events.append(random.choice([e for e in event_pool if e not in self.events]))

    def modify_trigger(self, event_pool):

        removed = self.events.pop(random.randint(0, len(self.events) - 1))
        self.events.append(random.choice([e for e in event_pool if e not in self.events and e != removed]))

    def remove_trigger(self):

        self.events.pop(random.randint(0, len(self.events) - 1))

    def modify_property_class(self, property_pool):

        self.property_class = random.choice([p for p in property_pool if p != self.property_class])

    def modify_coefficient(self, coefficient_pool):

        self.coefficient = random.choice([c for c in coefficient_pool if c != self.coefficient])

    def unique(self):
        ss = ''
        oo = sorted([e.id for e in self.events])
        for o in oo: ss += str(o)
        return ss + f'_{self.property_class.name()}_({self.coefficient})'

    def __repr__(self):
        return f"({[e.name() for e in self.events]}) -> {self.property_class.name()}(i+1) = {self.property_class.name()}(i) + ({self.coefficient}) * {self.property_class.name()}(i)"