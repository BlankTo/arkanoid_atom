from core.individual import Individual
from core.object import Object
from utils.various import ID_generator
from core.unexplained import Appearance, Disappearance, check_blink, check_disappearance, check_duplication, check_for_property0_changes, check_for_speed, check_multiple_holes_simple, check_multiple_holes_speed
from core.events import event_pool

from core.unexplained import PropertyChange

import math
import itertools


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

    #to_test_hypothesis = {}
    #next_to_test = {}

    print(f'population: {population}')
    print(f'present_objects:')
    for obj_id, obj in present_objects.items():
        print(f'\tobj_{obj_id}: {obj}')
    print(f'not_present_objects:')
    for obj_id, obj in not_present_objects.items():
        print(f'\tobj_{obj_id}: {obj}')

    for frame_id, patches in enumerate(patches_per_frame):
        if frame_id == 0: continue
        print(f'\n{frame_id}/{len(patches_per_frame)} - population: {len(population.keys())}')

        #print(f'population: {population}')
        #print(f'present_objects: {present_objects}')
        #print(f'not_present_objects: {not_present_objects}')

        unassigned_objects = [obj_id for obj_id in present_objects.keys()] # all objects of all individuals (some are shared)

        unassigned_patches = {ind_id: [p for p in patches] for ind_id in population.keys()} # list of unassigned patches for each individual

        # evaluate perfectly explainable patches (the ones that can be inferred from the current properties (for now: correct no speed, correct speed zero or correct speed))

        #print(f'unassigned_objects: {unassigned_objects}')
        #print(f'unassigned_patches: {unassigned_patches}')

        #print('\n--\n\ncheck perfect assignment')

        for patch in patches:
            #other_patches = [p for p in patches if p != patch]
            perfectly_assigned_objects = []

            #print('===============')
            #print(f'patch: {patch}')

            for obj_id in unassigned_objects:

                #print(f'obj_id: {obj_id} -> {present_objects[obj_id]}')

                prediction = present_objects[obj_id].prediction

                all_ok = True
                for property_class, value in patch.properties.items():

                    if prediction[property_class] != value:
                        all_ok = False

                #print(f'all_ok: {all_ok}')
                
                if all_ok:

                    present_objects[obj_id].update(frame_id, patch, prediction)
                    perfectly_assigned_objects.append(obj_id)

                    for ind_id, ind in population.items():
                        if obj_id in ind:
                            unassigned_patches[ind_id].remove(patch)

                    #print(f'population: {population}')
                    #print(f'present_objects: {present_objects}')
                    #print(f'not_present_objects: {not_present_objects}')
                    #print(f'unassigned_objects: {unassigned_objects}')
                    #print(f'unassigned_patches: {unassigned_patches}')

                    #break

            for obj_id in perfectly_assigned_objects: unassigned_objects.remove(obj_id)

        #print('end of perfect assignment')
        #print(f'population: {population}')
        #print(f'present_objects: {present_objects}')
        #print(f'not_present_objects: {not_present_objects}')
        #print(f'unassigned_objects: {unassigned_objects}')
        #print(f'unassigned_patches: {unassigned_patches}')

        ## evaluate possible solution for not perfectly explained patches (check if a first degree quantity can explain the diff, in that case the change happened in the frame before)
   
        #print('\n--\n\ntry speed')

        for patch in set([p for u_p in unassigned_patches.values() for p in u_p]):
            #other_patches = [p for p in patches if p != patch]

            #print(f'patch: {patch}')

            for obj_id in unassigned_objects:
                current_obj = present_objects[obj_id]

                #print(f'obj_id: {obj_id} -> {present_objects[obj_id]}')

                possible_unexplained = []

                # could be a change of speed # in future a change of one first degree quantity (like how speed is for pos but for the other properties too, less scripted and could involve accelaration by itself)

                is_speed, unexplained_dict, properties = check_for_speed(current_obj, patch, frame_id)
                if is_speed: possible_unexplained.append((unexplained_dict, properties))

                #print(f'is_speed: {is_speed}')

                # si potrebbero valutare anche i not_present_objects dal loro ultimo frame a quello corrente per valutare se esiste una first degree quantity che spiega il vuoto su piu frame

                new_inds = {}
                for ind_id, ind in population.items():
                    if obj_id in ind and patch in unassigned_patches[ind_id]:

                        for unexplained_dict, properties in possible_unexplained:

                            new_obj_id = obj_id_generator()
                            new_expl_dict = {k: [ex for ex in v] for k, v in current_obj.unexplained.items()}
                            for k, v in unexplained_dict.items():
                                if k in new_expl_dict.keys(): new_expl_dict[k].extend(v)
                                else: new_expl_dict[k] = v
                            present_objects[new_obj_id] = Object(current_obj.frames_id + [frame_id], current_obj.sequence + [patch], properties, new_expl_dict)

                            #print('============================')
                            #print('============================')
                            #print('============================')
                            #print(population)
                            #for iid in range(len(population)):
                            #    for k, v in events[iid].items():
                            #        print(f'{k}: {v}')

                            new_ind_id = ind_id_generator()
                            new_inds[new_ind_id] = [ob for ob in population[ind_id] if ob != obj_id] + [new_obj_id]

                            #ll = {}
                            #for ud in unexplained_dict.values():
                            #    for uc in ud:
                            #        if type(uc) == PropertyChange:
                            #            ll[uc.property_class] = {'value': uc.final_value, 'correct': True}
                            #next_to_test[new_obj_id] = {'p1': ll, 'base': ind_id, 'self': new_ind_id}

                            events[new_ind_id] = {(fid, new_obj_id if ob == obj_id else ob): v for (fid, ob), v in events[ind_id].items()}
                            unassigned_patches[new_ind_id] = [p for p in unassigned_patches[ind_id] if p != patch]

                            #print('---')
                            #print(population)
                            #for iid in range(len(population)):
                            #    for k, v in events[iid].items():
                            #        print(f'{k}: {v}')

                population |= new_inds

                #print(f'population: {population}')
                #print(f'present_objects: {present_objects}')
                #print(f'not_present_objects: {not_present_objects}')
                #print(f'unassigned_objects: {unassigned_objects}')
                #print(f'unassigned_patches: {unassigned_patches}')

        #print('end of try speed')
        #print(f'population: {population}')
        #print(f'present_objects: {present_objects}')
        #print(f'not_present_objects: {not_present_objects}')
        #print(f'unassigned_objects: {unassigned_objects}')
        #print(f'unassigned_patches: {unassigned_patches}')

        print(f'population: {population}')
        print(f'present_objects:')
        for obj_id, obj in present_objects.items():
            print(f'\tobj_{obj_id}: {obj}')
        print(f'not_present_objects:')
        for obj_id, obj in not_present_objects.items():
            print(f'\tobj_{obj_id}: {obj}')

        # evaluate patches and objects with unexplained changes (one time quantity change or blink or different number of p and o) (assignment based on property's proximity, until there are couples (all if the number of p and o is the same))
        
        # volendo qua si potrebbero valutare combinazioni per scomparsa/comparsa, ma forse esploderebbe
        # piu che altro occorrerebbe nel caso magari valutare anche la possibilita che un oggetto prima scomparso stia ricomparendo (oltre che il "nuovo oggetto compare")

        print('\n--\n\ntry unexplained')

        new_inds = {}
        for ind_id, ind in population.items():

            print(f'ind_id: {ind_id}')

            up = unassigned_patches[ind_id]
            uo = [o for o in unassigned_objects if o in ind]

            print(f'unassigned objects for ind_{ind_id}: {uo}')
            print(f'present_objects:')
            for obj_id, obj in present_objects.items():
                print(f'\tobj_{obj_id}: {obj}')
            print(f'unassigned patches for ind_{ind_id}: {up}')

            op_diff = []

            for obj_id in uo:
                pred = present_objects[obj_id].prediction

                for patch in up:

                    diff = compute_diff(pred, patch)

                    op_diff.append((obj_id, patch, diff))

            op_diff = sorted(op_diff, key= lambda x: x[2])

            #print(f'op_diff: {op_diff}')

            ao = []
            ap = []

            #print('diff assignment')
            
            for obj_id, patch, diff in op_diff:
                if obj_id not in ao and patch not in ap:
                    ao.append(obj_id)
                    ap.append(patch)

                    p0_did_change, unexplained_dict, properties = check_for_property0_changes(present_objects[obj_id], patch, frame_id)

                    present_objects[obj_id].update(frame_id, patch, properties)
                    present_objects[obj_id].add_unexplained(unexplained_dict)
                    
            #print(f'population: {population}')
            #print(f'present_objects: {present_objects}')
            #print(f'not_present_objects: {not_present_objects}')
            #print(f'unassigned_objects: {unassigned_objects}')
            #print(f'unassigned_patches: {unassigned_patches}')
            #print(f'ao: {ao}')
            #print(f'ap: {ap}')

            # evaluate remaining patches or objects (only one type of the two should remain) (if there are patches left they are new object appeared, else there are object left they disappear)

            last_objects = [ob for ob in uo if ob not in ao]
            last_patches = [p for p in up if p not in ap]

            #print(f'remaining objects: {last_objects}')
            #print(f'remaining patches for in_{ind_id}: {last_patches}')

            # disappearing objects

            for obj_id in last_objects:

                ##################################################################
#
#                #print(f'add obj_{obj_id} disappearance possibility')
#
#                disappearing_obj = present_objects.pop(obj_id)
#
#                it_disappeared, unexplained_dict, properties = check_disappearance(disappearing_obj, frame_id)
#                
#                disappearing_obj.update(frame_id, disappearing_obj.sequence[-1], properties)
#                disappearing_obj.add_unexplained(unexplained_dict)
#
#                not_present_objects[obj_id] = disappearing_obj
#
                ##################################################################

                current_obj = present_objects[obj_id]

                it_disappeared, unexplained_dict, properties = check_disappearance(current_obj, frame_id)

                if it_disappeared:
                    new_obj_id = obj_id_generator()
                    new_expl_dict = {k: [ex for ex in v] for k, v in current_obj.unexplained.items()}
                    for k, v in unexplained_dict.items():
                        if k in new_expl_dict.keys():
                            new_expl_dict[k].extend(v)
                        else:
                            new_expl_dict[k] = v

                    not_present_objects[new_obj_id] = Object(
                        current_obj.frames_id,
                        current_obj.sequence,
                        properties,
                        new_expl_dict
                    )

                    # Assign the new object to a new individual

                    new_ind_id = ind_id_generator()
                    new_inds[new_ind_id] = [ob for ob in population[ind_id] if ob != obj_id] + [new_obj_id]
                    events[new_ind_id] = {(fid, new_obj_id if ob == obj_id else ob): v for (fid, ob), v in events[ind_id].items()}
                    unassigned_patches[new_ind_id] = [] # if here, then there are no more unassigned patches for this individual

                ##################################################################

            # appearing objects

            for patch in last_patches:

                #print(f'patch: {patch}')

                assigned_to = None
                best_diff = math.inf

                for obj_id in not_present_objects.keys():
                    if obj_id in ind:

                        diff = compute_diff(not_present_objects[obj_id].prediction, patch)

                        if diff < best_diff:
                            best_diff = diff
                            assigned_to = obj_id

                #print(f'best match: {assigned_to}')

                if assigned_to: # create the solution for which an object reappeared

                    current_obj = not_present_objects[assigned_to]

                    # speed while disappeared

                    unexplained = []

                    # same speed it has

                    is_simple, unexplained_dict, properties = check_multiple_holes_simple(current_obj, patch, frame_id)

                    #print(f'is_simple: {is_simple}')

                    if is_simple: # reappearance of obj_id object in a new individual
                        unexplained.append((unexplained_dict, properties))

                    else: # a new speed

                        moved_with_new_speed, unexplained_dict, properties = check_multiple_holes_speed(current_obj, patch, frame_id)

                        #print(f'moved_with_new_speed: {moved_with_new_speed}')

                        if moved_with_new_speed: # reappearance of obj_id object in a new individual that obtained a new speed disappearing
                            unexplained.append((unexplained_dict, properties))

                    # blink
                    
                    it_blinked, unexplained_dict, properties = check_blink(current_obj, patch, frame_id)

                    #print(f'it_blinked: {it_blinked}')

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

                        #ààà for individuals that contains obj_id do:

                        new_ind_id = ind_id_generator()
                        new_inds[new_ind_id] = [ob for ob in population[ind_id] if ob != obj_id] + [new_obj_id]
                        events[new_ind_id] = {k: v for k, v in events[ind_id]}

                #print(f'population: {population}')
                #print(f'present_objects: {present_objects}')
                #print(f'not_present_objects: {not_present_objects}')
                #print(f'unassigned_objects: {unassigned_objects}')
                #print(f'unassigned_patches: {unassigned_patches}')

                # duplication of one object

                #print('duplication?')

                assigned_to = None
                best_diff = math.inf

                for obj_id in present_objects.keys():
                    if obj_id in ind:

                        diff = compute_diff(present_objects[obj_id].prediction, patch)

                        if diff < best_diff:
                            best_diff = diff
                            assigned_to = obj_id

                #print(f'best_match: {assigned_to}')

                current_obj = present_objects[assigned_to]

                is_duplicated, unexplained_dict, properties = check_duplication(current_obj, patch, frame_id)

                #print(f'is_duplicated: {is_duplicated}')

                if is_duplicated:

                    new_obj_id = obj_id_generator()
                    present_objects[new_obj_id] = Object([frame_id], [patch], properties, unexplained_dict)

                    #ààà for individuals that contains obj_id do:

                    new_ind_id = ind_id_generator()
                    new_inds[new_ind_id] = [ob for ob in population[ind_id]] + [new_obj_id]
                    events[new_ind_id] = {k: v for k, v in events[ind_id]}

                #print(f'population: {population}')
                #print(f'present_objects: {present_objects}')
                #print(f'not_present_objects: {not_present_objects}')
                #print(f'unassigned_objects: {unassigned_objects}')
                #print(f'unassigned_patches: {unassigned_patches}')

                # new object

                #print('new object')

                new_obj_id = obj_id_generator()
                present_objects[new_obj_id] = Object([frame_id], [patch], patch.properties)

                population[ind_id].append(new_obj_id)
        
                #print(f'population: {population}')
                #print(f'present_objects: {present_objects}')
                #print(f'not_present_objects: {not_present_objects}')
                #print(f'unassigned_objects: {unassigned_objects}')
                #print(f'unassigned_patches: {unassigned_patches}')

            #unassigned_objects = [ob for ob in unassigned_objects if ob not in ao]

        population |= new_inds

        ## event detection (in individual, cause it depends on the the assignment of all objects)

#        print(population)
#        print(to_test_hypothesis)
#
#        for tested_obj_id, info in to_test_hypothesis.items():
#            
#            correct = True
#            for property_class, val_and_test in info['p1'].items():
#                if not val_and_test['correct']:
#                    correct = False
#                    break
#
#            if correct:
#                print(f'removing father: {info["base"]}')
#                population.pop(info['base'])
#                events.pop(info['base'])
#                unassigned_patches.pop(info['base'])
#            else:
#                print(f'removing self: {info["self"]}')
#                population.pop(info['self'])
#                events.pop(info['self'])
#                unassigned_patches.pop(info['self'])
#
#        to_test_hypothesis = next_to_test
#        next_to_test = {}

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

                #if frame_id in current_obj.unexplained.keys():
                #    for expl in current_obj.unexplained[frame_id]:
                #        if expl is Appearance: current_events.append(Appearance())
                #        if expl is Disappearance: current_events.append(Disappearance())

                #if current_events: print(f'ind_{ind_id} obj_{obj_id} events for frame_{frame_id}: {current_events}')

                events[ind_id][(frame_id, obj_id)] = current_events

        print(f'population: {population}')
        print(f'present_objects:')
        for obj_id, obj in present_objects.items():
            print(f'\tobj_{obj_id}: {obj}')
        print(f'not_present_objects:')
        for obj_id, obj in not_present_objects.items():
            print(f'\tobj_{obj_id}: {obj}')

    all_obj = present_objects | not_present_objects
    population = [Individual({obj_id: obj for obj_id, obj in all_obj.items() if obj_id in ind}, events[ind_id], len(patches_per_frame)) for ind_id, ind in population.items()]

    return population



## (i+1) = a * (i) + b * (i) + c, a in [0, 1], b in [-2, -1, 0, 1, 2], c in [0, 1], avoiding (a=1, b=0, c=0) ?
