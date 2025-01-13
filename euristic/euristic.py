from core.individual import Individual
from core.object import Object
from utils.various import ID_generator, compute_diff
from core.unexplained import (
    check_blink, check_disappearance, check_duplication,
    check_for_property0_changes, check_for_speed,
    check_multiple_holes_simple, check_multiple_holes_speed,
    )
from core.rule import rule_trigger_and_check, rule_inference

import math

def euristic_initialization(patches_per_frame, debug= False):

    ind_id_generator = ID_generator()
    obj_id_generator = ID_generator()

    # initialization with one object per patch in the first frame

    present_objects = {obj_id_generator(): Object([0], [patch]) for patch in patches_per_frame[0]} # dict obj_id: obj
    population = {ind_id_generator(): [obj_id for obj_id in present_objects.keys()]} # list of individual, each individual is a list of objects_id
    not_present_objects = {} # dict obj_id: obj

    #

    for frame_id, patches in enumerate(patches_per_frame):
        if frame_id == 0: continue
        print(f'\n{frame_id}/{len(patches_per_frame)} - population: {len(population.keys())}')

        unassigned_objects = [obj_id for obj_id in present_objects.keys()] # all present objects of all individuals (some are shared between individuals)
        unassigned_patches = {ind_id: [p for p in patches] for ind_id in population.keys()} # list of unassigned patches for each individual

        #if debug:
        #    print(f'population: {population}')
        #    print(f'present_objects:')
        #    for obj_id, obj in present_objects.items():
        #        print(f'\tobj_{obj_id}: {obj}')
        #        print(f'\tn_rules: {len(obj.rules)}')
        #        for rid, rule in enumerate(obj.rules): print(f'\t\trule_{rid}:\n\t\tcauses: {rule.causes}\n\t\teffects: {rule.effects}\n\t\toffset: {rule.cause_offset}')
        #    print(f'not_present_objects:')
        #    for obj_id, obj in not_present_objects.items():
        #        print(f'\tobj_{obj_id}: {obj}')
        #        print(f'\tn_rules: {len(obj.rules)}')
        #        for rid, rule in enumerate(obj.rules): print(f'\t\trule_{rid}:\n\t\tcauses: {rule.causes}\n\t\teffects: {rule.effects}\n\t\toffset: {rule.cause_offset}')

            #print(f'unassigned_objects: {unassigned_objects}')
            #print(f'unassigned_patches: {unassigned_patches}')

        #

        # evaluate perfectly explainable patches (the ones that can be inferred from the current properties (for now: correct no speed, correct speed zero or correct speed))

        if debug: print('\nperfect')

        for pid, patch in enumerate(patches):
            if debug: print(f'\rpatch {pid+1}/{len(patches)}', end= "")
            other_patches = [p for p in patches if p != patch]

            perfectly_assigned_objects = []

            for obj_id in unassigned_objects:

                prediction = present_objects[obj_id].prediction

                all_ok = True
                for property_class, value in patch.properties.items():

                    if prediction[property_class] != value:
                        all_ok = False
                
                if all_ok: # if an object prediction correctly identifies a patch, then that patch is assigned to the object and marked as assigned for the individuals with that object

                    present_objects[obj_id].update(frame_id, patch, prediction, other_patches)
                    perfectly_assigned_objects.append(obj_id)

                    for ind_id, ind in population.items():
                        if obj_id in ind:
                            unassigned_patches[ind_id].remove(patch)

            for obj_id in perfectly_assigned_objects: unassigned_objects.remove(obj_id)

        #

        ## evaluate possible solution for Q1 changes (check if a first degree quantity can explain the diff, in that case the change happened in the frame before)

        if debug: print('\n\nQ1')

        pset = set([p for u_p in unassigned_patches.values() for p in u_p]) # set of all the unassigned patches of all individuals
        for pid, patch in enumerate(pset):
            if debug: print(f'\rpatch {pid+1}/{len(pset)}', end= "")
            other_patches = [p for p in patches if p != patch]

            for obj_id in unassigned_objects:
                #print(f'\nobj_{obj_id}\n')
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
                    new_obj.update(frame_id, patch, properties, other_patches)
                    new_obj.add_unexplained(unexplained_dict)
                    present_objects[new_obj_id] = new_obj

                    for ind_id, ind in population.items():
                        if obj_id in ind and patch in unassigned_patches[ind_id]:

                            new_ind_id = ind_id_generator()
                            new_inds[new_ind_id] = [ob for ob in population[ind_id] if ob != obj_id] + [new_obj_id]
                            unassigned_patches[new_ind_id] = [p for p in unassigned_patches[ind_id] if p != patch]

                population |= new_inds

        #

        # evaluate patches and objects with one time quantity change (assignment based on property's proximity, until there are couples)
        
        # volendo qua si potrebbero valutare combinazioni per scomparsa/comparsa, ma forse esploderebbe
        # piu che altro occorrerebbe nel caso magari valutare anche la possibilita che un oggetto prima scomparso stia ricomparendo (oltre che il "nuovo oggetto compare")

        if debug: print('\n\nremaining pairing')

        remaining_objects = {ind_id: [ob for ob in unassigned_objects if ob in ind] for ind_id, ind in population.items()}

        new_inds = {}
        for ind_pid, (ind_id, ind) in enumerate(population.items()):
            
            if debug: print(f'\rind {ind_pid+1}/{len(population)}', end= "")

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

                    p0_did_change, unexplained_dict, properties = check_for_property0_changes(present_objects[obj_id], patch, frame_id)

                    present_objects[obj_id].update(frame_id, patch, properties, [p for p in patches if p != patch]) #here
                    present_objects[obj_id].add_unexplained(unexplained_dict)

                    for ind_id in inds_with_same_pair:
                        remaining_objects[ind_id].remove(obj_id)
                        unassigned_patches[ind_id].remove(patch)

        #

        # evaluate remaining patches or objects (only one type of the two should remain) (if there are patches left they are new object appeared or previously disappeared objects reappeared, else if there are object left they disappear)

        if debug: print('\n\nremaining single')

        for ind_id, ind in population.items(): assert(not (remaining_objects[ind_id] and unassigned_patches[ind_id]))

        for ind_pid, (ind_id, ind) in enumerate(population.items()):
            
            if debug: print(f'\rind {ind_pid+1}/{len(population)}', end= "")

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
                        present_objects[new_obj_id] = Object(current_obj.frames_id + [frame_id], current_obj.sequence + [patch], properties, new_expl_dict)

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
                    present_objects[new_obj_id] = Object([frame_id], [patch], properties, unexplained_dict)

                    #here do it for each ind with obj_id and patch inside

                    new_ind_id = ind_id_generator()
                    new_inds[new_ind_id] = [ob for ob in population[ind_id]] + [new_obj_id]

                #

                # new object

                new_obj_id = obj_id_generator()
                present_objects[new_obj_id] = Object([frame_id], [patch], patch.properties)

                population[ind_id].append(new_obj_id)

        population |= new_inds

        #

        # existing rule trigger and check

        if debug: print('\n\nrule check')

        objs_to_remove = rule_trigger_and_check(present_objects, not_present_objects)

        for obj_id in objs_to_remove: # test the rules of each object, explain the unexplained that are effects of triggered rules and remove individuals with faulty rules
            
            if obj_id in present_objects: present_objects.pop(obj_id)
            else: not_present_objects.pop(obj_id)

            inds_to_remove = []
            for ind_id, ind in population.items():
                if obj_id in ind: inds_to_remove.append(ind_id)
            
            for ind_id in inds_to_remove:
                population.pop(ind_id)
                unassigned_patches.pop(ind_id)

        #

        # rule inference and check #here

        ## rule creation and maybe aggregation
        # 1) Check for events, unexplaineds and explaineds in frames[-n:] and create a rule with combinations of them as cause (each rule create a new individual with that rule)
        # 2) Leave the default (no rule and unexplained unexplained) untouched (indipendently of previous individual creation)
        # (next) 3) check rule equality between objects and form classes (if all the objects in two classes are the same, fuse them) with the common rules (rules in different classes could still count as one for the scoring)

        if debug: print('rule inference')

        new_inds = rule_inference(population, present_objects, not_present_objects, frame_id, ind_id_generator, obj_id_generator, debug= debug)
        population |= new_inds
        for new_ind_id in new_inds.keys(): unassigned_patches[new_ind_id] = []

        #

        # scoring and pruning (#here expand in order to use events and rules for scoring)

        # score = n°(unexplained) - n°(rules)
        # or
        # score = (n°(unexplained), n°(rules))

        ## think about leaving more space to the pruning
        # second chances or more
        # or
        # keeping the n best individuals
        # or
        # evaluate the score in different ways (no rule n° malus, invert scoring rules unexplained, or similar)

        # probablistic tournament 5 to 5 to 1

        # for now it's similar to a beam search over frames

        if debug: print('scoring')

        best_score = math.inf
        scores = []
        for ind_id, ind in population.items():
            total_unexplained = 0
            total_rules = 0

            ind_objects = [(obj_id, present_objects[obj_id] if obj_id in present_objects.keys() else not_present_objects[obj_id]) for obj_id in ind]

            for obj_id, obj in ind_objects:
                for frame_id, unexpl in obj.unexplained.items():
                    total_unexplained += len(unexpl)
                
                for rule in obj.rules:
                    total_rules += len(rule.effects) + 1

            score = total_unexplained + total_rules
            
            scores.append((ind_id, score))
            if score < best_score: best_score = score

        # removal of pruned individuals

        ind_to_remove = [ind_id for ind_id, score in scores if score != best_score]

        for ind_id in ind_to_remove:
                population.pop(ind_id)
                unassigned_patches.pop(ind_id)

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

    #

    ## conversion to Individual class

    all_obj = present_objects | not_present_objects
    final_population = []
    for ind_id, ind in population.items():
        object_dict = {}
        for obj_id, obj in all_obj.items():
            if obj_id in ind:
                object_dict[obj_id] = obj
        final_population.append(Individual(object_dict, len(patches_per_frame)))

    return final_population



## (i+1) = b * (i) + c, a in [-2, -1, 0, 1, 2], b in [-1, 0, 1] or ∀R
# -2v+b # inversione velocizzata
# -v+b # inversione con b=0
# b # start o stop
# v+b # modifica velocita con b!=0
# 2v+b # speed-up