from core.individual import Individual
from core.object import Object
from utils.various import ID_generator
from core.unexplained import check_blink, check_disappearance, check_duplication, check_for_property0_changes, check_for_speed, check_multiple_holes_simple, check_multiple_holes_speed
from core.events import event_pool

import math


def compute_diff(pred, patch):

    diff = 0

    for property_class, value in patch.properties.items():
        diff += abs(pred[property_class] - value)

    # valutare n di proprieta differenti?

    return diff


def euristic_initialization(patches_per_frame):

    ind_id_generator = ID_generator()
    obj_id_generator = ID_generator()

    present_objects = {obj_id_generator(): Object([0], [patch]) for patch in patches_per_frame[0]} # dict obj_id: obj
    population = {ind_id_generator(): [obj_id for obj_id in present_objects.keys()]} # list of individual, each individual is a list of objects_id
    not_present_objects = {} # dict obj_id: obj
    events = {ind_id: {} for ind_id in population.keys()}

    #

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

        #

        print(f'population: {population}')
        print(f'present_objects:')
        for obj_id, obj in present_objects.items():
            print(f'\tobj_{obj_id}: {obj}')
        print(f'not_present_objects:')
        for obj_id, obj in not_present_objects.items():
            print(f'\tobj_{obj_id}: {obj}')

        unassigned_objects = [obj_id for obj_id in present_objects.keys()] # all present objects of all individuals (some are shared between individuals)
        unassigned_patches = {ind_id: [p for p in patches] for ind_id in population.keys()} # list of unassigned patches for each individual

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
                            remaining_objects[ind_id] = [ob for ob in remaining_objects[ind_id] if ob != obj_id] + [ replacement_obj_id]
                            events[ind_id] = {(fid, new_obj_id if ob == obj_id else ob): v for (fid, ob), v in events[ind_id].items()}

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

        #

        # scoring and pruning (#here expand in order to use events and rules for scoring)

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
    population = [Individual({obj_id: obj for obj_id, obj in all_obj.items() if obj_id in ind}, events[ind_id], len(patches_per_frame)) for ind_id, ind in population.items()]

    return population



## (i+1) = a * (i) + b * (i) + c, a in [0, 1], b in [-2, -1, 0, 1, 2], c in [0, 1], avoiding (a=1, b=0, c=0) ?
