from utils.various import equal_collections
from core.unexplained import (
    UnexplainedSpecificChange, UnexplainedNumericalChange, PropertyChange,
    )
from core.events import Event

import itertools

class Phenomenon:

    def __init__(self, info):
        pass

    def test(self, phenomenon):
        pass

    def __repr__(self):
        pass

class SpecificUnexplainedPhenomenon(Phenomenon):

    def __init__(self, info):
        self.unexplained_class = info['unexplained_class']

    def test(self, phenomenon):
        return isinstance(phenomenon, self.unexplained_class)
    
    def __repr__(self):
        return self.unexplained_class.__name__
    
    def __eq__(self, other):
        if isinstance(other, SpecificUnexplainedPhenomenon): return self.unexplained_class == other.unexplained_class
        else: return False

class NumericalUnexplainedPhenomenon(Phenomenon):

    def __init__(self, info):
        self.property_class = info['property_class']
        self.a = info['a']
        self.b = info['b']

    def test(self, phenomenon):
        if isinstance(phenomenon, PropertyChange):
            return (phenomenon.final_value == self.a * phenomenon.previous_value + self.b)
        else: return False
    
    def __repr__(self):
        return f'{self.property_class.name()}(i+1) = {self.a} * {self.property_class.name()}(i) + {self.b}'
    
    def __eq__(self, other):
        if isinstance(other, NumericalUnexplainedPhenomenon): return (self.property_class == other.property_class and self.a == other.a and self.b == other.b)
        else: return False

class EventPhenomenon(Phenomenon):

    def __init__(self, info):
        self.event_class = info['event_class']

    def test(self, phenomenon):
        return isinstance(phenomenon, self.event_class)
    
    def __eq__(self, other):
        if isinstance(other, EventPhenomenon): return self.event_class == other.event_class
        else: return False
    
    def __repr__(self):
        return self.event_class.__name__

class Rule:

    def __init__(self, cause_offset, causes, effects):
        self.cause_offset = cause_offset  # Difference between effect frame and cause frame
        self.causes = causes[:]           # List of generalized causes as phenomenons
        self.effects = effects[:]         # List of effects as phenomenons

    def trigger(self, obj, frame_id):
        possible_causes = []
        possible_causes += obj.unexplained[frame_id] if frame_id in obj.unexplained.keys() else []
        possible_causes += obj.explained_unexplained[frame_id] if frame_id in obj.explained_unexplained.keys() else []
        possible_causes += obj.events[frame_id] if frame_id in obj.events.keys() else []
        if all([any([cause.test(pc) for pc in possible_causes]) for cause in self.causes]):
            return True, self.effects, self.cause_offset
        else: return False, None, None

    def __eq__(self, other):
        if not (isinstance(other, Rule)): return False
        if self.cause_offset != other.cause_offset: return False
        if not equal_collections(self.causes, other.causes): return False
        if not equal_collections(self.effects, other.effects): return False
        return True

    def __repr__(self):
        return f'rule\nwith causes: {self.causes}\nwith effects: {self.effects}\nafter {self.cause_offset} frames'

A_RANGE = [-1, 0, 1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6]
B_RANGE = [-1, 0, 1]

def convert_to_phenomenon(event_or_unexplained):

    if isinstance(event_or_unexplained, UnexplainedSpecificChange):
        return SpecificUnexplainedPhenomenon({'unexplained_class': event_or_unexplained.__class__})
    elif isinstance(event_or_unexplained, UnexplainedNumericalChange):
        previous = event_or_unexplained.previous_value
        final = event_or_unexplained.final_value
        if previous == 0:
            a = 0
            b = final
        else:
            perfect_a = None
            for try_a in A_RANGE:
                if final == try_a * previous:
                    perfect_a = try_a
                    break
            if perfect_a:
                a = perfect_a
                b = 0
            else:
                perfect_pair = None
                for try_a, try_b in itertools.product(A_RANGE, B_RANGE):
                    if final == try_a * previous + try_b:
                        perfect_pair = (try_a, try_b)
                        break
                if perfect_pair:
                    a, b = perfect_pair
                else:
                    return None
        return NumericalUnexplainedPhenomenon({'a': a, 'b': b, 'property_class': event_or_unexplained.property_class})
    elif issubclass(event_or_unexplained, Event):
        return EventPhenomenon({'event_class': event_or_unexplained})
    else:
        print('nah2')
        exit(0)

def rule_inference(population, present_objects, not_present_objects, frame_id, ind_id_generator, obj_id_generator, debug= False):

    new_inds = {}

    for ind_pid, (ind_id, ind) in enumerate(population.items()):

        if debug: print(f'\rind {ind_pid}/{len(population)}', end= "")

        all_ind_objs = [(obj_id, present_objects[obj_id] if obj_id in present_objects.keys() else not_present_objects[obj_id]) for obj_id in ind]

        for obj_id, obj in all_ind_objs:

            possible_cause_subset_per_frame = {}
            
            for cF in [frame_id-4, frame_id-3, frame_id-2, frame_id-1, frame_id]:

                possible_causes_per_frame = []

                if cF in obj.unexplained.keys():
                    for unexpl in obj.unexplained[cF]:
                        phenomenon = convert_to_phenomenon(unexpl)
                        if phenomenon: possible_causes_per_frame.append(phenomenon)

                if cF in obj.explained_unexplained.keys():
                    for expl in obj.explained_unexplained[cF]:
                        phenomenon = convert_to_phenomenon(expl)
                        if phenomenon: possible_causes_per_frame.append(phenomenon)
                
                if cF in obj.events.keys():
                    for event in obj.events[cF]:
                        phenomenon = convert_to_phenomenon(event)
                        if phenomenon: possible_causes_per_frame.append(phenomenon)
                
                possible_cause_subset_per_frame[cF] = [list(comb) for r in range(1, len(possible_causes_per_frame) + 1) for comb in itertools.combinations(possible_causes_per_frame, r)]


            for eF in [frame_id-2, frame_id-1, frame_id]:
                possible_effects = []
                if eF in obj.unexplained.keys():
                    for unexpl in obj.unexplained[eF]:
                        phenomenon = convert_to_phenomenon(unexpl)
                        if phenomenon: possible_effects.append(phenomenon)
                
                for effect_subset in [list(comb) for r in range(1, len(possible_effects) + 1) for comb in itertools.combinations(possible_effects, r)]:

                    for cF in [eF-2, eF-1, eF]:

                        for cause_subset in possible_cause_subset_per_frame[cF]:
                            if any([c.__eq__(e) for c in cause_subset for e in effect_subset]):
                                continue

                            new_rule = Rule(eF - cF, cause_subset, effect_subset)

                            new_ind_id = ind_id_generator()
                            new_obj_id = obj_id_generator()
                            
                            new_obj = obj.copy()
                            new_obj.add_rule(new_rule)
                            new_obj.explain(eF, effect_subset)
                            new_ind = [obid for obid in ind if obid != obj_id] + [new_obj_id]
                            
                            all_objects_temp = present_objects | not_present_objects
                            population_temp = population | new_inds

                            for ooid, oobj in all_objects_temp.items():
                                if new_obj == oobj:

                                    new_obj_id = ooid
                                    new_obj = oobj
                                    new_ind = [obid for obid in ind if obid != new_obj_id] + [ooid]
                                    break

                            new_inds[new_ind_id] = new_ind
                            if obj_id in present_objects.keys(): present_objects[new_obj_id] = new_obj
                            else: not_present_objects[new_obj_id] = new_obj

    if debug: print()

    return new_inds

def rule_trigger_and_check(present_objects, not_present_objects):

    all_objects = present_objects | not_present_objects

    objs_to_remove = []

    for obj_id, obj in all_objects.items():
        frame_length = len(obj.frames_id)
        for rule in obj.rules:
            for frame_id in range(frame_length):
                if frame_id + rule.cause_offset < frame_length and frame_id > frame_length - 5:
                    triggered, effects, offset = rule.trigger(obj, frame_id)
                    if triggered:
                        ok = obj.check_and_explain(frame_id + offset, effects)
                        if not ok:
                            objs_to_remove.append(obj_id)
                            break
            if obj_id in objs_to_remove: break

    return objs_to_remove