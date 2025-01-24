from core.object import Object
from core.property import Pos_x, Pos_y, Speed_x, Speed_y
from core.patch import Patch

class UnexplainedChange:
    pass

class UnexplainedNumericalChange(UnexplainedChange):
    pass

class UnexplainedSpecificChange(UnexplainedChange):
    pass

class PropertyChange(UnexplainedNumericalChange):

    def __init__(self, property_class, previous_value, final_value):
        self.property_class = property_class
        self.previous_value = previous_value
        self.final_value = final_value

    def copy(self):
        return PropertyChange(self.property_class, self.previous_value, self.final_value)
    
    def __repr__(self): return f'PropertyChange({self.property_class.name()}: {self.previous_value} -> {self.final_value})'

    def __eq__(self, other):
        if isinstance(other, PropertyChange): return self.property_class == other.property_class and self.final_value - self.previous_value == other.final_value - other.previous_value
        else: return False

    def my_hash(self):
        return ('PropertyChange', self.property_class, self.final_value - self.previous_value)

class Appearance(UnexplainedSpecificChange):

    def __init__(self):
        pass

    def copy(self):
        return Appearance()
    
    def __repr__(self): return 'Appearance'

    def __eq__(self, other):
        if isinstance(other, Appearance): return True
        else: return False

    def my_hash(self):
        return ('Appearance', None, None)

class Disappearance(UnexplainedSpecificChange):

    def __init__(self):
        pass

    def copy(self):
        return Disappearance()

    def __eq__(self, other):
        if isinstance(other, Disappearance): return True
        else: return False

    def my_hash(self):
        return ('Disappearance', None, None)
    
    def __repr__(self): return 'Disappearance'

class Duplication(UnexplainedSpecificChange):

    def __init__(self, from_obj):
        self.from_obj = from_obj

    def copy(self):
        return Duplication(self.from_obj)
    
    def __repr__(self): return f'Duplication(from {self.from_obj})'

    def __eq__(self, other):
        if isinstance(other, Duplication): return self.from_obj == other.from_obj

    def my_hash(self):
        return ('Duplication', self.from_obj.id, None) # this is wrong and just a placeholder

# change the dict keys to string
# define Property as mother class and Property_0 and Property_1
# Property_0's compute just return the new patch's property associated with the string of reference (starting with only Property_0 and in future expanding to Property_1)
# Property_1's compute compute the actual value change between the last two frames
# Property_0's effect return the same value
# Property_1's effect return the change and in which property
# then modify the function to test possible combinations Property_1's changes that could explain the diff and return all possible list of unexplaineds
def check_for_speed(obj, patch, frame_id):

    last_patch = obj.sequence[-1]
    last_properties = {k: v for k, v in obj.current_properties.items()}
    last_properties[Speed_x] = Speed_x.compute(last_patch, patch)
    last_properties[Speed_y] = Speed_y.compute(last_patch, patch)

    dummy_object = Object([obj.frames_id[-1]], [last_patch], last_properties)

    all_ok = True
    for property_class, value in patch.properties.items():
        if dummy_object.prediction[property_class] != value:
            all_ok = False
            break

    if all_ok:
        unexplained = []
        if Speed_x in obj.current_properties.keys():
            if obj.current_properties[Speed_x] != last_properties[Speed_x]:
                unexplained.append(PropertyChange(Speed_x, obj.current_properties[Speed_x], last_properties[Speed_x]))
        else: unexplained.append(PropertyChange(Speed_x, 0, last_properties[Speed_x]))
        if Speed_y in obj.current_properties.keys():
            if obj.current_properties[Speed_y] != last_properties[Speed_y]:
                unexplained.append(PropertyChange(Speed_y, obj.current_properties[Speed_y], last_properties[Speed_y]))
        else: unexplained.append(PropertyChange(Speed_y, 0, last_properties[Speed_y]))
        if not unexplained: return False, None, None
        return True, {frame_id - 1: unexplained}, dummy_object.prediction
    else: return False, None, None

def check_for_property0_changes(obj, patch, frame_id):

    unexplained = []
    new_properties = {k: v for k, v in obj.prediction.items()}

    for property_class, value in patch.properties.items():
        if obj.prediction[property_class] != value:
            unexplained.append(PropertyChange(property_class, obj.current_properties[property_class], value))
            new_properties[property_class] = value

    if unexplained: return True, {frame_id: unexplained}, new_properties
    else: return False, {}, new_properties


def check_disappearance(obj, frame_id):
    return True, {frame_id: [Disappearance()]}, obj.current_properties

# same for this one
def check_multiple_holes_simple(obj, patch, frame_id):

    starting_frame_id = obj.frames_id[-1]
    dummy_object = Object([obj.frames_id[-1]], [obj.sequence[-1]], obj.current_properties)

    for i in range(starting_frame_id + 1, frame_id):

        dummy_object.update(i, Patch('dummy', dummy_object.prediction), dummy_object.prediction)

    all_ok = True
    for property_class, value in patch.properties.items():
        if dummy_object.prediction[property_class] != value:
            all_ok = False
            break

    if all_ok: return True, {frame_id: [Appearance(frame_id)]}, dummy_object.prediction
    else: return False, None, None

# same for this one
def check_multiple_holes_speed(obj, patch, frame_id):

    dummy_object = Object([obj.frames_id[-1]], [obj.sequence[-1]], obj.current_properties)

    starting_frame_id = obj.frames_id[-1]
    last_patch = obj.sequence[-1]
    last_properties = {k: v for k, v in obj.current_properties.items()}
    last_properties[Speed_x] = Speed_x.compute(last_patch, patch) / (frame_id - starting_frame_id)
    last_properties[Speed_y] = Speed_y.compute(last_patch, patch) / (frame_id - starting_frame_id)

    for i in range(starting_frame_id + 1, frame_id):

        dummy_object.update(i, Patch('dummy', dummy_object.prediction), dummy_object.prediction)

    all_ok = True
    for property_class, value in patch.properties.items():
        if dummy_object.prediction[property_class] != value:
            all_ok = False
            break

    if all_ok: return True, {starting_frame_id: [PropertyChange(Speed_x, obj.current_properties[Speed_x], dummy_object.prediction[Speed_x]), PropertyChange(Speed_y, obj.current_properties[Speed_y], dummy_object.prediction[Speed_y])], frame_id: Appearance()}, dummy_object.prediction
    else: return False, None, None


# same
def check_blink(obj, patch, frame_id):

    last_properties = {k: v for k, v in obj.current_properties.items()}

    for property_class, value in patch.properties.items():
        last_properties[property_class] = value

    return True, {frame_id: [Disappearance(), Appearance()]}, last_properties

# same
def check_duplication(obj, patch, frame_id):

    last_properties = {k: v for k, v in obj.current_properties.items()}

    for property_class, value in patch.properties.items():
        last_properties[property_class] = value

    return True, {frame_id: [Duplication(obj)]}, last_properties