class Object:

    def __init__(self, frames_id, sequence, current_properties= None, unexplained= {}):

        self.frames_id = [fid for fid in frames_id]

        self.sequence = [p for p in sequence]

        if current_properties is None: self.current_properties = sequence[-1].properties
        else: self.current_properties = current_properties

        self.unexplained = {k: [ex.copy() for ex in v] for k, v in unexplained.items()}

        self.prediction = self.compute_next()

    def copy(self):
        return Object(self.frames_id, self.sequence, self.current_properties, self.unexplained)

    def compute_next(self):

        new_properties = {property_class: value for property_class, value in self.current_properties.items()}

        for property_class in self.current_properties.keys():
            for prop_to_modify, change in property_class.effects(self.current_properties).items():
                new_properties[prop_to_modify] += change

        return new_properties
    
    def update(self, frame_id, patch, new_properties):

        self.frames_id.append(frame_id)
        self.sequence.append(patch)
        self.current_properties = new_properties

        self.prediction = self.compute_next()

    def add_unexplained(self, unexplained_dict):
        for frame_id, unexplained in unexplained_dict.items():
            if frame_id in self.unexplained.keys(): self.unexplained[frame_id].extend([ex.copy() for ex in unexplained])
            else: self.unexplained[frame_id] = [ex.copy() for ex in unexplained]

#    def __eq__(self, other):
#        
#        match(type(other)):
#            case Object:
#                if self.frames_id != other.frames_id: return False
#                if self.sequence != other.sequence: return False
#                if self.unexplained != other.expla
#                if self.current_properties == other.current_properties: return False
#                return True

    def __repr__(self):
        ss = f'[{self.sequence[0].description}'
        for patch in self.sequence[1:]:
            ss += f', {patch.description}'
        ss += '] -> {'
        for prop_class, val in self.current_properties.items():
            ss += f'({prop_class.name()}: {val})'
        ss += '} - {'
        for frame_id, expl in self.unexplained.items():
            ss += f'{frame_id}: {expl} |'
        ss += '}'
        return ss