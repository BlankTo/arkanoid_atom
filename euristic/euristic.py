from core.individual import Individual
from core.object import Object
from utils.various import ID_generator, compute_diff
from core.unexplained import (
    check_blink, check_disappearance, check_duplication,
    check_for_property0_changes, check_for_speed,
    check_multiple_holes_simple, check_multiple_holes_speed,
    )
from core.rule import new_infer_rules
from core.property import Shape_x, Shape_y

import math

SURVIVAL_TIME = 2

def remove_inds(population, unassigned_patches, unassigned_objects, present_objects, not_present_objects, survival_dict, inds_to_remove):

    for ind_id in inds_to_remove:
        population.pop(ind_id)
        unassigned_patches.pop(ind_id)
        survival_dict.pop(ind_id)

    # and of objects that are not in kept individuals

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

def euristic_initialization(patches_per_frame, global_events_per_frame, resume_population= None, debug= False):

    if resume_population is None:

        ind_id_generator = ID_generator()
        obj_id_generator = ID_generator()

        # initialization with one object per patch in the first frame

        present_objects = {obj_id_generator(): Object(frames_id= [0], sequence= [patch], properties= {0: patch.properties}, global_events= {0: global_events_per_frame[0]}) for patch in patches_per_frame[0]} # dict obj_id: obj
        population = {ind_id_generator(): [obj_id for obj_id in present_objects.keys()]} # list of individual, each individual is a list of objects_id
        not_present_objects = {} # dict obj_id: obj

        starting_frame_id = 1

    else:

        starting_frame_id = 0
        max_ind_id = 0
        max_obj_id = 0

        population = {}
        all_objects = {}

        for ind_id, ind in resume_population.items():

            ind_obj_ids = []

            if ind_id > max_ind_id: max_ind_id = ind_id

            for obj_id, obj in ind.object_dict.items():

                ind_obj_ids.append(obj_id)

                if obj_id > max_obj_id: max_obj_id = obj_id

                if obj_id not in all_objects.keys(): all_objects[obj_id] = obj

                if obj.frames_id[-1] > starting_frame_id: starting_frame_id = obj.frames_id[-1]

            population[ind_id] = ind_obj_ids

        ind_id_generator = ID_generator(max_ind_id)
        obj_id_generator = ID_generator(max_obj_id)

        present_objects = {}
        not_present_objects = {}

        for obj_id, obj in all_objects.items():
            if obj.frames_id[-1] == starting_frame_id: present_objects[obj_id] = obj
            else: not_present_objects[obj_id] = obj
        
        starting_frame_id += 1

    survival_dict = {ind_id: SURVIVAL_TIME for ind_id in population.keys()} # ind_id: survival_ages_remaining

    #
    if not debug: print('\n\n\n')
    for frame_id_enum, (patches, global_events) in enumerate(zip(patches_per_frame[starting_frame_id:], global_events_per_frame[starting_frame_id:])):
        frame_id = frame_id_enum + starting_frame_id
        if debug: print(f'\n\n---------------------------------------\nframe: {frame_id}/{len(patches_per_frame)} - population: {len(population.keys())}')
        else: print(f'\033[K\033[F\033[K\033[F\033[K\033[F\033[K\033[F\033[K\n\n---------------------------------------\nframe: {frame_id}/{len(patches_per_frame)} - population: {len(population.keys())}')

        unassigned_objects = [obj_id for obj_id in present_objects.keys()] # all present objects of all individuals (some are shared between individuals)
        unassigned_patches = {ind_id: [p for p in patches] for ind_id in population.keys()} # list of unassigned patches for each individual

        # evaluate perfectly explainable patches (the ones that can be inferred from the current properties (for now: correct no speed, correct speed zero or correct speed))

        if debug: print('\nperfect')

        for pid, patch in enumerate(patches):
            if debug: print(f'\rpatch {pid+1}/{len(patches)}', end= "")
            other_patches = [p for p in patches if p != patch]

            perfectly_assigned_objects = []
            assigned_patches = {}
            inds_to_remove = []

            for obj_id in unassigned_objects:
                current_obj = present_objects[obj_id]

                prediction = current_obj.prediction
                predicted_explained = current_obj.predicted_explained

                all_ok = True
                for property_class, value in patch.properties.items():

                    if prediction[property_class] != value:
                        all_ok = False
                
                if all_ok: # if an object prediction correctly identifies a patch, then that patch is assigned to the object and marked as assigned for the individuals with that object
                    
                    new_properties = {fid: {k: v for k, v in prop.items()} for fid, prop in current_obj.properties.items()}
                    new_properties[frame_id] = prediction
                    current_obj.update(frame_id, patch, new_properties, other_patches, global_events)
                    current_obj.add_explained({frame_id - 1: predicted_explained})
                    perfectly_assigned_objects.append(obj_id)

                    for ind_id, ind in population.items():
                        if obj_id in ind:
                            if ind_id in assigned_patches.keys():
                                if patch not in assigned_patches[ind_id]: assigned_patches[ind_id].append(patch)
                                else:
                                    inds_to_remove.append(ind_id)
                                    continue
                            else: assigned_patches[ind_id] = [patch]
                            unassigned_patches[ind_id].remove(patch)

            remove_inds(population, unassigned_patches, unassigned_objects, present_objects, not_present_objects, survival_dict, inds_to_remove)
            
            for obj_id in perfectly_assigned_objects:
                if obj_id in unassigned_objects: unassigned_objects.remove(obj_id)

        #

        ## evaluate possible solution for Q1 changes (check if a first degree quantity can explain the diff, in that case the change happened in the frame before)

        if debug: print(f'\n\nQ1 - population: {len(population)}')

        pset = set([p for u_p in unassigned_patches.values() for p in u_p]) # set of all the unassigned patches of all individuals
        for pid, patch in enumerate(pset):
            if debug: print(f'\rpatch {pid+1}/{len(pset)}', end= "")
            other_patches = [p for p in patches if p != patch]

            assigned_objects = []
            new_unassigned_objects = []

            for obj_id in unassigned_objects:
                current_obj = present_objects[obj_id]

                is_speed, is_confirmed, unexplained_dict, new_properties = check_for_speed(current_obj, patch, frame_id, patches_per_frame[frame_id + 1] if frame_id + 1 < len(patches_per_frame) else None)
                if is_speed:

                    if is_confirmed:
                        
                        original_inds = []
                        inds_to_branch = []
                        for ind_id, ind in population.items():
                            if obj_id in ind:
                                if patch in unassigned_patches[ind_id]: original_inds.append(ind_id)
                                else: inds_to_branch.append(ind_id)

                        if inds_to_branch:

                            replacement_obj_id = obj_id_generator()
                            replacement_obj = current_obj.copy()
                            present_objects[replacement_obj_id] = replacement_obj
                            new_unassigned_objects.append(replacement_obj_id)

                            for ind_id in inds_to_branch:
                                population[ind_id] = [ob for ob in population[ind_id] if ob != obj_id] + [replacement_obj_id]

                        current_obj.update(frame_id, patch, new_properties, other_patches, global_events)
                        current_obj.add_unexplained(unexplained_dict)
                        assigned_objects.append(obj_id)

                        for ind_id in original_inds:
                            unassigned_patches[ind_id].remove(patch)

                    else:

                        new_obj_id = obj_id_generator()
                        new_obj = current_obj.copy()
                        new_obj.update(frame_id, patch, new_properties, other_patches, global_events)
                        new_obj.add_unexplained(unexplained_dict)
                        present_objects[new_obj_id] = new_obj

                        new_inds = {}

                        for ind_id, ind in population.items():
                            if obj_id in ind and patch in unassigned_patches[ind_id]:

                                new_ind_id = ind_id_generator()
                                new_inds[new_ind_id] = [ob for ob in population[ind_id] if ob != obj_id] + [new_obj_id]
                                unassigned_patches[new_ind_id] = [p for p in unassigned_patches[ind_id] if p != patch]

                        population |= new_inds
                        for ind_id in new_inds.keys(): survival_dict[ind_id] = SURVIVAL_TIME

            for obj_id in assigned_objects: unassigned_objects.remove(obj_id)
            for obj_id in new_unassigned_objects: unassigned_objects.append(obj_id)

        #

        # evaluate patches and objects with one time quantity change (assignment based on property's proximity, until there are couples)
        
        # volendo qua si potrebbero valutare combinazioni per scomparsa/comparsa, ma forse esploderebbe
        # piu che altro occorrerebbe nel caso magari valutare anche la possibilita che un oggetto prima scomparso stia ricomparendo (oltre che il "nuovo oggetto compare")

        if debug: print(f'\n\nremaining pairing - population: {len(population)}')

        remaining_objects = {ind_id: [ob for ob in unassigned_objects if ob in ind] for ind_id, ind in population.items()}

        op_best_assignments = {} # (obj_id, patch): (times_assigned, list_of_individuals)
        for ind_pid, (ind_id, ind) in enumerate(population.items()):
            
            if debug: print(f'\rind {ind_pid+1}/{len(population)}', end= "")

            op_diff = []

            for obj_id in remaining_objects[ind_id]:
                current_object = present_objects[obj_id]

                for patch in unassigned_patches[ind_id]:
                    diff = compute_diff(current_object.properties[frame_id - 1], patch) #here

                    op_diff.append((obj_id, patch, diff))

            op_diff = sorted(op_diff, key= lambda x: x[2])

            object_with_best_assignment = []
            patch_with_best_assigned = []
            
            for obj_id, patch, diff in op_diff:
                if obj_id not in object_with_best_assignment and patch not in patch_with_best_assigned:

                    object_with_best_assignment.append(obj_id)
                    patch_with_best_assigned.append(patch)

                    if obj_id in op_best_assignments.keys():
                        if patch in op_best_assignments[obj_id].keys():
                            oba = op_best_assignments[obj_id][patch]
                            op_best_assignments[obj_id][patch] = (oba[0] + 1, oba[1] + [ind_id])
                        else:
                            op_best_assignments[obj_id][patch] = (1, [ind_id])
                    else:
                        op_best_assignments[obj_id] = {patch: (1, [ind_id])}

        all_remaining_objects = set()
        for ro in remaining_objects.values(): all_remaining_objects.update(ro)

        for obj_id in list(all_remaining_objects):
            if obj_id in op_best_assignments.keys():
                best_patch = None
                best_times = 0
                best_ind_list = None

                for patch, (times, ind_list) in op_best_assignments[obj_id].items():
                    if times > best_times:
                        best_times = times
                        best_patch = patch
                        best_ind_list = ind_list

                for patch, (times, ind_list) in op_best_assignments[obj_id].items():
                    if patch != best_patch:

                        # branching new object with that patch and q0 change, for all ind in ind_list

                        replacement_obj_id = obj_id_generator()
                        present_objects[replacement_obj_id] = present_objects[obj_id].copy()

                        p0_did_change, unexplained_dict, new_properties = check_for_property0_changes(present_objects[replacement_obj_id], patch, frame_id)

                        present_objects[replacement_obj_id].update(frame_id, patch, new_properties, [p for p in patches if p != patch], global_events)
                        present_objects[replacement_obj_id].add_unexplained(unexplained_dict)

                        for ind_id in ind_list:
                            population[ind_id] = [ob for ob in population[ind_id] if ob != obj_id] + [replacement_obj_id]
                            remaining_objects[ind_id] = [ob for ob in remaining_objects[ind_id] if ob != obj_id]
                            unassigned_patches[ind_id].remove(patch)

                # update of original object with best_patch and q0 change

                p0_did_change, unexplained_dict, new_properties = check_for_property0_changes(present_objects[obj_id], best_patch, frame_id)

                present_objects[obj_id].update(frame_id, best_patch, new_properties, [p for p in patches if p != best_patch], global_events)
                present_objects[obj_id].add_unexplained(unexplained_dict)

                for ind_id in best_ind_list:
                    remaining_objects[ind_id].remove(obj_id)
                    unassigned_patches[ind_id].remove(best_patch)


        # evaluate remaining patches or objects (only one type of the two should remain) (if there are patches left they are new object appeared or previously disappeared objects reappeared, else if there are object left they disappear)

        if debug: print(f'\n\nremaining single - population: {len(population)}')

        new_inds = {}

        for ind_id, ind in population.items(): assert(not (remaining_objects[ind_id] and unassigned_patches[ind_id]))

        for ind_pid, (ind_id, ind) in enumerate(population.items()):
            
            if debug: print(f'\rind {ind_pid+1}/{len(population)}', end= "")

            # disappearing objects

            disappeared = []

            for obj_id in remaining_objects[ind_id]:

                it_disappeared, unexplained_dict, properties = check_disappearance(present_objects[obj_id], frame_id)

                if it_disappeared:

                    disappearing_obj = present_objects.pop(obj_id)
                    disappearing_obj.add_unexplained(unexplained_dict)
                    not_present_objects[obj_id] = disappearing_obj

                    disappeared.append(obj_id)
                    
            for obj_id in disappeared:
                for ro in remaining_objects.values():
                    if obj_id in ro: ro.remove(obj_id)

            #

            # appearing objects (not yet tested)

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
                        new_properties = current_obj.properties
                        new_properties[frame_id] = properties
                        present_objects[new_obj_id] = Object(current_obj.frames_id + [frame_id], current_obj.sequence + [patch], new_properties, new_expl_dict)

                        #here do it for each ind with obj_id and patch inside

                        new_ind_id = ind_id_generator()
                        new_inds[new_ind_id] = [ob for ob in population[ind_id] if ob != obj_id] + [new_obj_id]

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
                    present_objects[new_obj_id] = Object([frame_id], [patch], {frame_id: properties}, unexplained_dict)

                    #here do it for each ind with obj_id and patch inside

                    new_ind_id = ind_id_generator()
                    new_inds[new_ind_id] = [ob for ob in population[ind_id]] + [new_obj_id]

                #

                # new object

                new_obj_id = obj_id_generator()
                present_objects[new_obj_id] = Object([frame_id], [patch], {frame_id: patch.properties})

                population[ind_id].append(new_obj_id)

        population |= new_inds
        for ind_id in new_inds.keys(): survival_dict[ind_id] = SURVIVAL_TIME

        #

        # rules
        ind_rule_score = {}
        for ind_id, ind in population.items(): ind_rule_score[ind_id] = new_infer_rules(ind, present_objects, not_present_objects, frame_id)
        #print(ind_rule_score)
        #

        # scoring and pruning

        if debug: print(f'\n\nscoring - population: {len(population)}')

        tuple_score = []
        ind_id_score_tuple = []
        for ind_pid, (ind_id, ind) in enumerate(population.items()):
            if debug: print(f'\rind {ind_pid+1}/{len(population)}', end= "")
            total_unexplained = 0

            ind_objects = [(obj_id, present_objects[obj_id] if obj_id in present_objects.keys() else not_present_objects[obj_id]) for obj_id in ind]

            for obj_id, obj in ind_objects:
                for unexpl in obj.unexplained.values():
                    total_unexplained += len(unexpl)
            
            explained_score, rule_score = ind_rule_score[ind_id]
            #tuple_score.append((total_unexplained, explained_score, rule_score))
            #tuple_score.append((explained_score, total_unexplained, rule_score))
            #tuple_score.append((explained_score + total_unexplained, rule_score))
            tuple_score.append((explained_score + total_unexplained + rule_score))
            ind_id_score_tuple.append(ind_id)

        sort_idx = sorted(range(len(tuple_score)), key=lambda i: tuple_score[i])
        tuple_score = [tuple_score[i] for i in sort_idx]
        ind_id_score_tuple = [ind_id_score_tuple[i] for i in sort_idx]

        # removal of pruned individuals

        inds_to_remove = [ind_id_score_tuple[i] for i in range(len(ind_id_score_tuple)) if tuple_score[i] > tuple_score[0]]
        #inds_to_remove = ind_id_score_tuple[1:]
        #inds_to_remove = []

        #probabilistic survival of inds_to_remove ?

        new_inds_to_remove = []
        for ind_id in survival_dict.keys():
            if ind_id in inds_to_remove:
                if survival_dict[ind_id] > 0:
                    survival_dict[ind_id] -= 1
                else: new_inds_to_remove.append(ind_id)
            else: survival_dict[ind_id] = SURVIVAL_TIME
        inds_to_remove = new_inds_to_remove
        remove_inds(population, unassigned_patches, unassigned_objects, present_objects, not_present_objects, survival_dict, inds_to_remove)
        
        #

        #if frame_id == 20:
        #    for ind_id, ind in population.items():
        #        print(f'ind_{ind_id}')
        #        for obj_id in ind:
        #            current_obj = present_objects[obj_id] if obj_id in present_objects.keys() else not_present_objects[obj_id]
        #            if all('paddle' in p.description for p in current_obj.sequence):
        #                print(f'\n----\nind_{ind_id}\n')
        #                print(current_obj.sequence[0].description)
        #                print('unexplained')
        #                for ffid, something in current_obj.unexplained.items():
        #                    print(f'frame_{ffid}: {something}')
        #                print('explained_unexplained')
        #                for ffid, something in current_obj.explained_unexplained.items():
        #                    print(f'frame_{ffid}: {something}')
        #                print('events')
        #                for ffid, something in current_obj.events.items():
        #                    print(f'frame_{ffid}: {something}')
        #                print('global_events')
        #                for ffid, something in current_obj.global_events.items():
        #                    print(f'frame_{ffid}: {something}')
        #                print('rules')
        #                for rule in current_obj.rules:
        #                    print(f'{rule.my_hash()}')
        #    exit()

    ## conversion to Individual class

    scores_dict = {ind_id_score_tuple[i]: tuple_score[i] for i in range(len(ind_id_score_tuple)) if tuple_score[i] == tuple_score[0]}

    all_obj = present_objects | not_present_objects
    final_population = []
    for ind_id, ind in population.items():
        if ind_id in scores_dict.keys():
            object_dict = {}
            for obj_id, obj in all_obj.items():
                if obj_id in ind:
                    object_dict[obj_id] = obj
            final_population.append((Individual(object_dict, len(patches_per_frame)), scores_dict[ind_id]))

    return final_population

def summarize_into_prototypes(final_individual):
    """
    Groups objects contained in the final individual into prototypes based on:
      1) The exact same set of rules (hashed by my_hash).
      2) The "const" or "var" behavior of each property across the object's frames.
    
    Then, it refines each prototype by checking the shapes (Shape_x, Shape_y) of the 
    objects in it, specifically in the object's last frame:
      - If all have the same shape and >1 objects, mark same_shape=True.
      - If all have the same shape and exactly 1 object, same_shape=None.
      - If all have distinct shapes, keep them together as one prototype with same_shape=True.
      - If there are subgroups with the same shape (some repeated shapes, some not),
        split the prototype into smaller prototypes by shape:
          * Each subgroup of size > 1 => same_shape=True
          * Each subgroup of size = 1 => same_shape=None
      - Remove the original prototype entry, and add the newly created ones.

    Finally, prints out each prototype in a human-readable way.
    """

    # --- STEP 1: Build the initial prototypes by (rules_signature, property_behavior_signature)
    prototypes = {}  # Dict[(rules_signature, prop_behavior_signature), list_of_obj_ids]
    
    for obj_id, obj in final_individual.object_dict.items():
        # 1. Compute rules_signature
        if hasattr(obj, 'rules') and obj.rules:
            rules_signature = tuple(sorted(rule.my_hash() for rule in obj.rules))
        else:
            rules_signature = tuple()
        
        # 2. Compute property behavior signature
        frames = sorted(obj.properties.keys())
        all_props = set()
        for fid in frames:
            all_props.update(obj.properties[fid].keys())
        
        prop_behavior = {}
        for prop in all_props:
            values = []
            for fid in frames:
                if prop in obj.properties[fid]:
                    values.append(obj.properties[fid][prop])
            behavior = 'const' if values and all(v == values[0] for v in values) else 'var'
            try:
                prop_name = prop.name()
            except Exception:
                prop_name = prop.__name__
            prop_behavior[prop_name] = behavior
        
        prop_behavior_signature = tuple(sorted(prop_behavior.items()))
        
        key = (rules_signature, prop_behavior_signature)
        if key not in prototypes:
            prototypes[key] = []
        prototypes[key].append(obj_id)
    
    # --- STEP 2: Refine each prototype by shape
    #     We'll build a new dict that replaces or subdivides prototypes based on shape grouping.
    refined_prototypes = {}
    proto_counter = 1  # just for display/enumeration
    
    for (rules_sig, prop_sig), obj_ids in prototypes.items():
        # Gather each object's final shape
        shape_dict = {}  # (shape_x_val, shape_y_val) -> list of obj_ids
        for oid in obj_ids:
            obj = final_individual.object_dict[oid]
            last_fid = obj.frames_id[-1]
            sx = obj.properties[last_fid][Shape_x]
            sy = obj.properties[last_fid][Shape_y]
            shape_val = (sx, sy)
            if shape_val not in shape_dict:
                shape_dict[shape_val] = []
            shape_dict[shape_val].append(oid)
        
        # Decide how to handle
        if len(shape_dict) == 1:
            # All objects have exactly the same shape
            shape_val = next(iter(shape_dict.keys()))  # the single key
            grp = shape_dict[shape_val]
            if len(grp) > 1:
                # multiple objects, same shape
                same_shape_flag = True
            else:
                # single object
                same_shape_flag = None
            
            # Keep them as one prototype
            refined_prototypes[proto_counter] = {
                'rules_signature': rules_sig,
                'prop_behavior_signature': prop_sig,
                'obj_ids': grp,
                'same_shape': same_shape_flag
            }
            proto_counter += 1
        
        elif len(shape_dict) == len(obj_ids):
            # Each object has a distinct shape
            # => keep them all in one prototype, same_shape=True
            refined_prototypes[proto_counter] = {
                'rules_signature': rules_sig,
                'prop_behavior_signature': prop_sig,
                'obj_ids': obj_ids,
                'same_shape': True
            }
            proto_counter += 1
        
        else:
            # We have subgroups of repeated shapes, but not all are the same shape.
            # => Split each shape subgroup into its own prototype.
            for shape_val, group_obj_ids in shape_dict.items():
                if len(group_obj_ids) > 1:
                    ss_flag = True
                else:
                    ss_flag = None
                
                refined_prototypes[proto_counter] = {
                    'rules_signature': rules_sig,
                    'prop_behavior_signature': prop_sig,
                    'obj_ids': group_obj_ids,
                    'same_shape': ss_flag
                }
                proto_counter += 1
    
    # --- STEP 3: Print the refined prototypes in a readable way.
    print("\n--- Prototipi Raggruppati (Refined by Shape) ---\n")
    for pid in sorted(refined_prototypes.keys()):
        proto_data = refined_prototypes[pid]
        
        rules_signature = proto_data['rules_signature']
        prop_behavior_signature = proto_data['prop_behavior_signature']
        obj_ids = proto_data['obj_ids']
        same_shape_flag = proto_data['same_shape']
        
        print(f"Prototipo {pid}:")
        
        # Print original rules from one sample object
        sample_obj_id = obj_ids[0]
        sample_obj = final_individual.object_dict[sample_obj_id]
        
        print("  Regole (originali):")
        if hasattr(sample_obj, 'rules') and sample_obj.rules:
            sorted_rules = sorted(sample_obj.rules, key=lambda r: r.my_hash())
            for rule in sorted_rules:
                print(f"    - {repr(rule)}")
        else:
            print("    (Nessuna regola)")
        
        print("  Firma (usata per il raggruppamento):")
        if rules_signature:
            print("    ", rules_signature)
        else:
            print("    (Nessuna regola)")
        
        print("  Comportamento proprietà:")
        if prop_behavior_signature:
            for prop_name, behavior in prop_behavior_signature:
                print(f"    - {prop_name}: {behavior}")
        else:
            print("    (Nessuna proprietà)")
        
        print(f"  Oggetti appartenenti: {obj_ids}")
        print(f"  same_shape = {same_shape_flag}")
        print("-" * 50)
