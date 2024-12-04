from copy import deepcopy

class Realization:

    def __init__(self, sequence, reference_object, properties= None):
        self.sequence = sequence
        self.reference_object = reference_object
        if properties is None: self.properties = deepcopy(sequence[-1].properties)
        else: self.properties = deepcopy(properties) # property_name: {'value': value, 'k': [list of possible k], 'all_k': bool}

    def length(self): return len(self.sequence)

    def validate(self, new_element, other_elements):

        last = self.sequence[-1]

        for rule in self.reference_object.rules:

            triggered = all(event.check(last, [new_element], other_elements) for event in rule.events)

            #TODO maybe compute realization properties before returning, all that are used in the rules

            if not triggered:
                return Realization(self.sequence + [new_element], self.reference_object, self.properties)
            
            #TODO create class property with function to compute it from two elements

            # 
            
            #if rule.property_name in self.properties.keys(): prop0 = self.properties[rule.property_name]['value']
            #else:
            #    self.properties[self.property_name]

        
        # k computation and check #TODO

        return ... # returning 'no', 'all_k' or a set of possible k values