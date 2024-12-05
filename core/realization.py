
class Realization:

    def __init__(self, reference_object, sequence, properties= None):

        self.reference_object = reference_object
        self.sequence = [e for e in sequence]

        if properties is None:
            assert(len(self.sequence) == 1)
            self.properties = {}

        else: self.properties = properties # property_class: {'last_value': value, 'k': 'all_k' or k}

    def length(self): return len(self.sequence)

    def validate(self, new_element, other_elements):

        new_properties = {pc: {k: v for k, v in d.items()} for pc, d in self.properties.items()}

        if len(self.sequence) == 1:

            for property_class in self.reference_object.get_properties_class():

                new_properties[property_class] = {
                                                    'last_value': property_class.compute(self.sequence[0], new_element, other_elements),
                                                    'k': 'all_k'
                                                    }
        
        else:

            last = self.sequence[-1]

            for rule in self.reference_object.rules:
                property_class = rule.property_class

                new_property_value = property_class.compute(last, new_element, other_elements)

                if all(event.check(last, new_element, other_elements) for event in rule.events):

                    if rule.coefficient == 0:

                        if new_property_value == self.properties[property_class]['last_value']: continue
                        else: return None

                    else:

                        new_k = (new_property_value - self.properties[property_class]['last_value']) / rule.coefficient

                        if self.properties[property_class]['k'] == 'all_k': new_properties[property_class]['k'] = new_k
                        elif new_k != self.properties[property_class]['k']: return None

                new_properties[property_class]['last_value'] = new_property_value

        return Realization(self.reference_object, self.sequence + [new_element], new_properties)