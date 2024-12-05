
class Realization:

    def __init__(self, reference_object, sequence, properties= None):

        self.reference_object = reference_object
        self.sequence = [e for e in sequence]

        if properties is None:
            assert(len(self.sequence) == 1)
            self.properties = {k: v for k, v in sequence[0].properties.items()}

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

    def validate(self, new_element, other_elements):

        log = ''

        log += '-----------------------------------------\n'
        log += '-----------------------------------------\n'
        log += f'{self} + [{new_element.description}]\n'
        for key in new_element.properties.keys():
            log += f'{key}: {self.properties[key]} -> {new_element.properties[key]}\n'

        new_properties = {pc: {k: v for k, v in d.items()} if type(d) == dict else d for pc, d in self.properties.items()}

        if len(self.sequence) == 1:

            for property_class in self.reference_object.get_properties_class():

                new_properties[property_class] = {
                                                    'last_value': property_class.compute(self.sequence[0], new_element, other_elements),
                                                    'k': 'all_k'
                                                    }
                
                for k, v in new_element.properties.items(): new_properties[k] = v
        
        else:

            last = self.sequence[-1]
            properties_coefficients = {}

            for property_class in self.reference_object.get_properties_class():
                property_composite_coefficient = 0

                for rule in self.reference_object.rules:
                    if rule.property_class == property_class:
                        if all(event.check(last, new_element, other_elements) for event in rule.events):

                            property_composite_coefficient += rule.coefficient

                properties_coefficients[property_class] = property_composite_coefficient

            base_properties_changes = {}
            updated_properties = {}

            for property_class, property_composite_coefficient in properties_coefficients.items():

                new_property_value = property_class.compute(last, new_element, other_elements)

                log += f'{property_class.name()}: a= {property_composite_coefficient}, value: {self.properties[property_class]["last_value"]} -> {new_property_value}\n'

                if property_composite_coefficient == 0:
                    if self.properties[property_class]["last_value"] == new_property_value: new_k = 'all_k'
                    else: return None
                else: new_k = (new_property_value - self.properties[property_class]['last_value']) / property_composite_coefficient

                if self.properties[property_class]['k'] != 'all_k':
                    if property_composite_coefficient == 'all_k': new_k = self.properties[property_class]['k']
                    elif new_k != self.properties[property_class]['k']: return None

                log += f'old_k: {self.properties[property_class]["k"]} -> new_k: {new_k}\n'

                updated_properties[property_class] = {'last_value': new_property_value, 'k': new_k}

                for property_name, changes in property_class.effects(new_property_value, self.properties).items():

                    if property_name in base_properties_changes.keys(): base_properties_changes[property_name] += changes
                    else: base_properties_changes[property_name] = changes

            for key in self.properties.keys():
                if type(key) == str:

                    log += f'{key}\n'

                    if key in base_properties_changes.keys():
                        if new_element.properties[key] != self.properties[key] + base_properties_changes[key]: return None
                        else: log += f'{new_element.properties[key]} == {self.properties[key]} + {base_properties_changes[key]}\n'
                    elif new_element.properties[key] != self.properties[key]: return None
                    else: log += f'{new_element.properties[key]} == {self.properties[key]}\n'

#            for property_name, changes in base_properties_changes.items():
#
#                if new_element.properties[property_name] == new_properties[property_name] + changes:
#                    new_properties[property_name] = new_element.properties[property_name]
#                else: return None

            for property_class, new_dict in updated_properties.items(): new_properties[property_class] = new_dict

        new_real = Realization(self.reference_object, self.sequence + [new_element], new_properties)
        #print(log)
        #print(f'{new_real} is valid for {self.reference_object}')
        return new_real

        return Realization(self.reference_object, self.sequence + [new_element], new_properties)
    
    def __repr__(self) -> str:
        ss = f'[{self.sequence[0].description}'
        for e in self.sequence[1:]: ss += f', {e.description}'
        return ss + ']'