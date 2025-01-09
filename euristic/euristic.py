from core.individual import Individual
from core.object import Object
from utils.various import ID_generator
from core.unexplained import (
    check_blink, check_disappearance, check_duplication,
    check_for_property0_changes, check_for_speed,
    check_multiple_holes_simple, check_multiple_holes_speed,
    UnexplainedSpecificChange, UnexplainedNumericalChange, PropertyChange,
    )
from core.events import event_pool, Event

import math
import itertools


def compute_diff(pred, patch):

    diff = 0

    for property_class, value in patch.properties.items():
        diff += abs(pred[property_class] - value)

    return diff

def equal_collections(list1, list2):
    if len(list1) != len(list2):
        return False
    for obj1 in list1:
        if not any(obj1 == obj2 for obj2 in list2):
            return False
    return True

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
        self.causes = causes[:]           # List of generalized causes
        self.effects = effects[:]         # List of effects categorized as numerical or specific

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

def rule_inference(population, present_objects, not_present_objects, events, rules, frame_id, ind_id_generator, obj_id_generator):

    new_inds = {}
    new_events = {}
    new_rules = {}

    all_objects = present_objects | not_present_objects

    for ind_id, ind in population.items():

        events_for_ind = events[ind_id]

        all_ind_objs = [(obj_id, present_objects[obj_id] if obj_id in present_objects.keys() else not_present_objects[obj_id]) for obj_id in ind]

        for obj_id, obj in all_ind_objs:

            possible_cause_subset_per_frame = {}
            
            for cF in [frame_id-4, frame_id-3, frame_id-2, frame_id-1, frame_id]:

                possible_causes_per_frame = []

                if cF in obj.unexplained.keys():
                    for unexpl in obj.unexplained[cF]:
                        phenomenon = convert_to_phenomenon(unexpl)
                        if phenomenon: possible_causes_per_frame.append(phenomenon)
                
                for (ev_fid, ev_oid), event_list in events_for_ind.items():
                    if ev_fid == cF and ev_oid == obj_id:
                        for event in event_list:
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

                            #print('----------------')
                            #print('testing')
                            #print(f'causes: {cause_subset}')
                            #print(f'effects: {effect_subset}')

                            new_rule = Rule(eF - cF, cause_subset, effect_subset)

                            in_rules = False
                            if (ind_id, obj_id) in rules.keys():
                                in_rules = True
                                if new_rule in rules[(ind_id, obj_id)]:
                                    print(f'the rule already exist in rules: {new_rule}')
                                    continue

                            if (ind_id, obj_id) in new_rules.keys():
                                if new_rule in new_rules[(ind_id, obj_id)]:
                                    print(f'the rule already exist in new_rules: {new_rule}')
                                    continue

                            for iid, iind in population.items():
                                if iid != ind_id:
                                    if equal_collections([all_objects[i] for i in iind], [all_objects[i] for i in ind]):
                                        if equal_collections(rules[(iid, obj_id)] + [new_rule], rules[(ind_id, obj_id)]):
                                            print(f'adding this rule would create a duplicate individual')
                                            exit(0)
                                            continue

                            new_ind_id = ind_id_generator()
                            new_obj_id = obj_id_generator()

                            new_inds[new_ind_id] = [obid for obid in ind if obid != obj_id] + [new_obj_id]
                            
                            new_obj = obj.copy()
                            new_obj.explain(eF, effect_subset)
                            if obj_id in present_objects.keys(): present_objects[new_obj_id] = new_obj
                            else: not_present_objects[new_obj_id] = new_obj

                            #here

                            new_events[new_ind_id] = {(fid, obid): [ev for ev in ev_list] for (fid, obid), ev_list in events_for_ind.items()}

                            base = rules[(ind_id, obj_id)][:] if in_rules else []
                            if (new_ind_id, obj_id) in new_rules.keys(): new_rules[(new_ind_id, obj_id)].extend(base + [new_rule])
                            else: new_rules[(ind_id, obj_id)] = base + [new_rule]
        
            #if frame_id == 2: exit(0)

    return new_inds, new_events, new_rules

def euristic_initialization(patches_per_frame, debug= False):

    ind_id_generator = ID_generator()
    obj_id_generator = ID_generator()

    present_objects = {obj_id_generator(): Object([0], [patch]) for patch in patches_per_frame[0]} # dict obj_id: obj
    population = {ind_id_generator(): [obj_id for obj_id in present_objects.keys()]} # list of individual, each individual is a list of objects_id
    not_present_objects = {} # dict obj_id: obj
    events = {ind_id: {} for ind_id in population.keys()}
    rules = {}

    #

    if debug:
        print(f'initial population: {population}')
        print(f'initial present_objects:')
        for obj_id, obj in present_objects.items():
            print(f'\tobj_{obj_id}: {obj}')
        print(f'initial not_present_objects:')
        for obj_id, obj in not_present_objects.items():
            print(f'\tobj_{obj_id}: {obj}')

    #

    for frame_id, patches in enumerate(patches_per_frame):
        if frame_id == 0: continue
        print(f'\n{frame_id}/{len(patches_per_frame)} - population: {len(population.keys())}')

        unassigned_objects = [obj_id for obj_id in present_objects.keys()] # all present objects of all individuals (some are shared between individuals)
        unassigned_patches = {ind_id: [p for p in patches] for ind_id in population.keys()} # list of unassigned patches for each individual

        if debug:
            print(f'population: {population}')
            print(f'present_objects:')
            for obj_id, obj in present_objects.items():
                print(f'\tobj_{obj_id}: {obj}')
            print(f'not_present_objects:')
            for obj_id, obj in not_present_objects.items():
                print(f'\tobj_{obj_id}: {obj}')

            print(f'unassigned_objects: {unassigned_objects}')
            print(f'unassigned_patches: {unassigned_patches}')

        #

        # evaluate perfectly explainable patches (the ones that can be inferred from the current properties (for now: correct no speed, correct speed zero or correct speed))

        for patch in patches:
            
            perfectly_assigned_objects = []

            for obj_id in unassigned_objects:

                prediction = present_objects[obj_id].prediction

                all_ok = True
                for property_class, value in patch.properties.items():

                    if prediction[property_class] != value:
                        all_ok = False
                
                if all_ok:

                    present_objects[obj_id].update(frame_id, patch, prediction)
                    perfectly_assigned_objects.append(obj_id)

                    for ind_id, ind in population.items():
                        if obj_id in ind:
                            unassigned_patches[ind_id].remove(patch)

                    #break #here

            for obj_id in perfectly_assigned_objects: unassigned_objects.remove(obj_id)

        #

        ## evaluate possible solution for Q1 changes (check if a first degree quantity can explain the diff, in that case the change happened in the frame before)

        for patch in set([p for u_p in unassigned_patches.values() for p in u_p]):

            for obj_id in unassigned_objects:
                current_obj = present_objects[obj_id]

                possible_unexplained = []

                # could be a change of speed # in future a change of one first degree quantity (like how speed is for pos but for the other properties too, less scripted and could involve accelaration by itself)

                is_speed, unexplained_dict, properties = check_for_speed(current_obj, patch, frame_id)
                if is_speed: possible_unexplained.append((unexplained_dict, properties))

                # si potrebbero valutare anche i not_present_objects dal loro ultimo frame a quello corrente per valutare se esiste una first degree quantity che spiega il vuoto su piu frame

                new_inds = {}

                for unexplained_dict, properties in possible_unexplained:

                    new_obj_id = obj_id_generator()
                    new_obj = present_objects[obj_id].copy()
                    new_obj.update(frame_id, patch, properties)
                    new_obj.add_unexplained(unexplained_dict)
                    present_objects[new_obj_id] = new_obj

                    for ind_id, ind in population.items():
                        if obj_id in ind and patch in unassigned_patches[ind_id]:

                            new_ind_id = ind_id_generator()
                            new_inds[new_ind_id] = [ob for ob in population[ind_id] if ob != obj_id] + [new_obj_id]
                            events[new_ind_id] = {(fid, new_obj_id if ob == obj_id else ob): v for (fid, ob), v in events[ind_id].items()}
                            for (iid, oid), rule_list in rules.items():
                                if iid == ind_id:
                                    if oid == obj_id: rule_list[(new_ind_id, new_obj_id)] = rule_list[(ind_id, obj_id)]
                                    else: rule_list[(new_ind_id, oid)] = rule_list[(ind_id, oid)]
                            unassigned_patches[new_ind_id] = [p for p in unassigned_patches[ind_id] if p != patch]

                population |= new_inds

        #

        # evaluate patches and objects with one time quantity change (assignment based on property's proximity, until there are couples)
        
        # volendo qua si potrebbero valutare combinazioni per scomparsa/comparsa, ma forse esploderebbe
        # piu che altro occorrerebbe nel caso magari valutare anche la possibilita che un oggetto prima scomparso stia ricomparendo (oltre che il "nuovo oggetto compare")

        remaining_objects = {ind_id: [ob for ob in unassigned_objects if ob in ind] for ind_id, ind in population.items()}

        new_inds = {}
        for ind_id, ind in population.items():

            op_diff = []

            for obj_id in remaining_objects[ind_id]:
                pred = present_objects[obj_id].prediction

                for patch in unassigned_patches[ind_id]:

                    diff = compute_diff(pred, patch)

                    op_diff.append((obj_id, patch, diff))

            op_diff = sorted(op_diff, key= lambda x: x[2])
            
            for obj_id, patch, diff in op_diff:
                if obj_id in remaining_objects[ind_id] and patch in unassigned_patches[ind_id]:
                    
                    inds_with_same_pair = []
                    inds_with_different_patches = []
                    for ind_id, ro in remaining_objects.items():

                        if obj_id in ro:
                            if patch in unassigned_patches[ind_id]: inds_with_same_pair.append(ind_id)
                            else: inds_with_different_patches.append(ind_id)

                    if inds_with_different_patches:

                        replacement_obj_id = obj_id_generator()
                        present_objects[replacement_obj_id] = present_objects[obj_id].copy()

                        for ind_id in inds_with_different_patches:

                            population[ind_id] = [ob for ob in population[ind_id] if ob != obj_id] + [replacement_obj_id]
                            remaining_objects[ind_id] = [ob for ob in remaining_objects[ind_id] if ob != obj_id] + [replacement_obj_id]
                            #events[ind_id] = {(fid, new_obj_id if ob == obj_id else ob): v for (fid, ob), v in events[ind_id].items()}

                    p0_did_change, unexplained_dict, properties = check_for_property0_changes(present_objects[obj_id], patch, frame_id)

                    present_objects[obj_id].update(frame_id, patch, properties) #here
                    present_objects[obj_id].add_unexplained(unexplained_dict)

                    for ind_id in inds_with_same_pair:
                        remaining_objects[ind_id].remove(obj_id)
                        unassigned_patches[ind_id].remove(patch)

        #

        # evaluate remaining patches or objects (only one type of the two should remain) (if there are patches left they are new object appeared or previously disappeared objects reappeared, else if there are object left they disappear)

        for ind_id, ind in population.items(): assert(not (remaining_objects[ind_id] and unassigned_patches[ind_id]))

        for ind_id, ind in population.items():

            # disappearing objects

            disappeared = []

            for obj_id in remaining_objects[ind_id]:

                it_disappeared, unexplained_dict, properties = check_disappearance(present_objects[obj_id], frame_id)

                if it_disappeared:

                    disappeared.append(obj_id)

                    disappearing_obj = present_objects.pop(obj_id)

                    disappearing_obj.add_unexplained(unexplained_dict)

                    not_present_objects[obj_id] = disappearing_obj
                    
            for obj_id in disappeared:
                for ro in remaining_objects.values():
                    if obj_id in ro: ro.remove(obj_id)

            #

            # appearing objects

            for patch in unassigned_patches[ind_id]:

                # reappearing objects

                assigned_to = None
                best_diff = math.inf

                for obj_id in not_present_objects.keys():
                    if obj_id in ind:

                        diff = compute_diff(not_present_objects[obj_id].prediction, patch)

                        if diff < best_diff:
                            best_diff = diff
                            assigned_to = obj_id

                # magari provare i primi n più simili (2?)

                if assigned_to: # search for a solution that explains the object reappearing

                    current_obj = not_present_objects[assigned_to]

                    unexplained = []

                    #

                    # speed while disappeared

                    is_simple, unexplained_dict, properties = check_multiple_holes_simple(current_obj, patch, frame_id)
                    if is_simple: unexplained.append((unexplained_dict, properties)) # same speed it has
                    else: # try a new speed (obtained on disappearance)

                        moved_with_new_speed, unexplained_dict, properties = check_multiple_holes_speed(current_obj, patch, frame_id)
                        if moved_with_new_speed: unexplained.append((unexplained_dict, properties))

                    #

                    # blink
                    
                    it_blinked, unexplained_dict, properties = check_blink(current_obj, patch, frame_id)
                    if it_blinked: # teleportation mantaining properties (properties changed saved in unexplained)
                        unexplained.append((unexplained_dict, properties))

                    #

                    for unexplained_dict, properties in unexplained:

                        new_obj_id = obj_id_generator()
                        new_expl_dict = {k: [ex for ex in v] for k, v in current_obj.unexplained.items()}
                        for k, v in unexplained_dict.items():
                            if k in new_expl_dict.keys(): new_expl_dict[k].extend(v)
                            else: new_expl_dict[k] = v
                        present_objects[new_obj_id] = Object(current_obj.frames_id + [frame_id], current_obj.sequence + [patch], properties, new_expl_dict)

                        #here do it for each ind with obj_id and patch inside

                        new_ind_id = ind_id_generator()
                        new_inds[new_ind_id] = [ob for ob in population[ind_id] if ob != obj_id] + [new_obj_id]
                        events[new_ind_id] = {k: v for k, v in events[ind_id]}
                        for (iid, oid), rule_list in rules.items():
                            if iid == ind_id:
                                if oid == obj_id: rule_list[(new_ind_id, new_obj_id)] = rule_list[(ind_id, obj_id)]
                                else: rule_list[(new_ind_id, oid)] = rule_list[(ind_id, oid)]

                #

                # duplication of one object

                assigned_to = None
                best_diff = math.inf

                for obj_id in present_objects.keys():
                    if obj_id in ind:

                        diff = compute_diff(present_objects[obj_id].prediction, patch)

                        if diff < best_diff:
                            best_diff = diff
                            assigned_to = obj_id

                current_obj = present_objects[assigned_to]

                is_duplicated, unexplained_dict, properties = check_duplication(current_obj, patch, frame_id)
                if is_duplicated:

                    new_obj_id = obj_id_generator()
                    present_objects[new_obj_id] = Object([frame_id], [patch], properties, unexplained_dict)

                    #here do it for each ind with obj_id and patch inside

                    new_ind_id = ind_id_generator()
                    new_inds[new_ind_id] = [ob for ob in population[ind_id]] + [new_obj_id]
                    events[new_ind_id] = {k: v for k, v in events[ind_id]}
                    for (iid, oid), rule_list in rules.items():
                        if iid == ind_id:
                            if oid == obj_id: rule_list[(new_ind_id, new_obj_id)] = rule_list[(ind_id, obj_id)]
                            else: rule_list[(new_ind_id, oid)] = rule_list[(ind_id, oid)]

                #

                # new object

                new_obj_id = obj_id_generator()
                present_objects[new_obj_id] = Object([frame_id], [patch], patch.properties)

                population[ind_id].append(new_obj_id)

        population |= new_inds

        #

        # event detection

        for ind_id, ind in population.items():

            ind_objects = [(obj_id, present_objects[obj_id] if obj_id in present_objects.keys() else not_present_objects[obj_id]) for obj_id in ind]
            
            for obj_id, current_obj in ind_objects:
                previous_patch = current_obj.sequence[-2]
                current_patch = current_obj.sequence[-1]
                other_patches = [ob.sequence[-1] for ob_id, ob in ind_objects if ob_id != obj_id]

                current_events = []
                for event in event_pool:
                    if event.check(previous_patch, current_patch, other_patches):
                        current_events.append(event)

                events[ind_id][(frame_id, obj_id)] = current_events

        #

        # rule inference and check #here

        ## rule creation and maybe aggregation
        # when a new unexplained is added
        # 1) Check if a rule already explain it, if yes skip this part
        # 2) Check for events in frames[-n:] and unexplained in frames[-n:-1] and create a rule with combinations of them as cause (each rule create a new individual with that rule)
        # 3) Leave the default (no rule and unexplained unexplained) untouched (indipendently of previous individual creation)
        # 4) (future) check rule equality between objects and form classes (if all the objects in two classes are the same, fuse them) with the common rules (rules in different classes could still count as one for the scoring)

        #here

#        new_inds, new_events, new_rules = rule_inference(population, present_objects, not_present_objects, events, {}, frame_id, ind_id_generator, obj_id_generator)
#
#        population |= new_inds
#        events |= new_events
#        rules |= new_rules
#        for new_ind_id in new_inds.keys(): unassigned_patches[new_ind_id] = []

        #

        # scoring and pruning (#here expand in order to use events and rules for scoring)

        # score = n°(unexplained) - n°(unexplained explained by rules) - n°(rules)
        # or
        # score = (n°(unexplained) - n°(unexplained explained by rules), n°(rules))

        ## think about leaving more space to the pruning
        # second chances or more
        # or
        # keeping the n best individuals
        # or
        # evaluate the score in different ways (no rule n° malus, invert scoring rules unexplained, or similar)

        best_score = math.inf
        scores = []
        for ind_id, ind in population.items():
            score = 0

            ind_objects = [(obj_id, present_objects[obj_id] if obj_id in present_objects.keys() else not_present_objects[obj_id]) for obj_id in ind]

            for obj_id, obj in ind_objects:
                for frame_id, unexpl in obj.unexplained.items():
                    score += len(unexpl)
            
            scores.append((ind_id, score))
            if score < best_score: best_score = score

        ind_to_remove = [ind_id for ind_id, score in scores if score != best_score]

        for ind_id in ind_to_remove:
                population.pop(ind_id)
                events.pop(ind_id)
                unassigned_patches.pop(ind_id)

        pair_to_remove = []
        for (iid, oid), rule_list in rules.items():
            if iid in ind_to_remove: pair_to_remove.append((iid, oid))
        for (iid, oid) in pair_to_remove: rules.pop((iid, oid))

        objs_to_keep = []
        for ind in population.values():
            objs_to_keep.extend(ind)
        objs_to_keep = set(objs_to_keep)

        present_to_remove = []
        for obj_id in present_objects.keys():
            if obj_id not in objs_to_keep: present_to_remove.append(obj_id)
        for obj_id in present_to_remove:
            present_objects.pop(obj_id)

        not_present_to_remove = []
        for obj_id in not_present_objects.keys():
            if obj_id not in objs_to_keep: not_present_to_remove.append(obj_id)
        for obj_id in not_present_to_remove:
            not_present_objects.pop(obj_id)

        for obj_id in present_to_remove + not_present_to_remove:
            if obj_id in unassigned_objects: unassigned_objects.remove(obj_id)

    #

    all_obj = present_objects | not_present_objects
    final_population = []
    for ind_id, ind in population.items():
        object_dict = {}
        rules_dict = {}
        for obj_id, obj in all_obj.items():
            if obj_id in ind:
                object_dict[obj_id] = obj
                if (ind_id, obj_id) in rules.keys(): rules_dict[obj_id] = rules[(ind_id, obj_id)]
        final_population.append(Individual(object_dict, events[ind_id], rules_dict, len(patches_per_frame)))

    return final_population



## (i+1) = b * (i) + c, a in [-2, -1, 0, 1, 2], b in [-1, 0, 1] or ∀R
# -2v+b # inversione velocizzata
# -v+b # inversione con b=0
# b # start o stop
# v+b # modifica velocita con b!=0
# 2v+b # speed-up