import math
import itertools

if __name__ == '__main__':

    import sys
    import os
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.append(project_root)

    from core.individual import Individual
    from core.object import Object
    from core.rule import Rule
    from core.events import Contact_With_Something_T, Contact_With_Something_B, Contact_With_Something_L, Contact_With_Something_R
    from core.property import Speed_x, Speed_y
    from utils.various import load_elements_per_frame, ID_generator

from core.realization import Realization
from core.events import Contact_With_Something_T, Contact_With_Something_B, Contact_With_Something_L, Contact_With_Something_R
from core.property import Speed_x, Speed_y


class FitnessEvaluator:

    @staticmethod
    def evaluate(population, frames):

        for ind_i, individual in enumerate(population):
            #print('--------------------------------')
            print(f'individual {ind_i+1}/{len(population)}') # - id: {individual.id}')

            if individual.fitness is not None: continue

            individual_score = 0

            elements_usage = [{} for _ in range(len(frames))]

            #for obj in individual.objects:
            for i_o, obj in enumerate(individual.objects):
                #print(f'object {i_o+1}/{len(individual.objects)}: {obj}')

                best_object_score = -math.inf
                best_sequence = None

                for e0, (e1_i, e1) in itertools.product(frames[0], enumerate(frames[1])):

                    #if e0.description != 'ball' or e1.description != 'ball': continue

                    #print(f'{e0.id} -> {e0.description}, {e1.id} -> {e1.description}')

                    sequence = [e0, e1]
                    current_others = frames[1][:e1_i] + frames[1][e1_i+1:]
                    properties = {k: v for k, v in e1.properties.items()}
                    k_dict = {Speed_x: Speed_x.compute(e0, e1, current_others), Speed_y: Speed_y.compute(e0, e1, current_others)}
                    #print(k_dict.items())
                    #exit()
                    properties[Speed_x] = k_dict[Speed_x]
                    properties[Speed_y] = k_dict[Speed_y]
                    events = [[], []]

                    for event in [Contact_With_Something_T, Contact_With_Something_B, Contact_With_Something_L, Contact_With_Something_R]:
                        if event.check(e0, e1, current_others): events[1].append(event)

                    object_score = 0

                    for frame_id in range(2, len(frames) - 1):

                        triggered_rules = []
                        properties_changes = {}

                        for rule in obj.rules:

                            triggered, effects = rule.effects(events[frame_id - 1])
                            
                            triggered_rules.append(triggered)

                            #if triggered: print(f'{[rule.events]} triggered')

                            for property_class, coeff in effects.items():
                                #print((property_class.name(), coeff))
                                if property_class in properties_changes.keys(): properties_changes[property_class] += coeff
                                else: properties_changes[property_class] = coeff

                        n_triggered = sum(triggered_rules)

                        cc = 0

                        for property_class, coeff in properties_changes.items():
                            properties[property_class] += coeff * k_dict[property_class]
                            cc += coeff * k_dict[property_class]

                        base_properties_changes = {}

                        #print('modified base properties:')

                        for property_class, value in properties.items():
                                
                            for prop_to_modify, change in property_class.effects(properties).items():

                                #print((prop_to_modify.name(), change))

                                if prop_to_modify in base_properties_changes.keys(): base_properties_changes[prop_to_modify] += change
                                else: base_properties_changes[prop_to_modify] = change
                        
                        for property_class, change in base_properties_changes.items():
                            properties[property_class] += change

                        best_score = -math.inf
                        best_idx = None

                        for e_i, e in enumerate(frames[frame_id]):

                            score = 0
                            total_diff = 0

                            for property_class, value in e.properties.items():
                                total_diff += abs(properties[property_class] - value)

                            score -= total_diff

                            if n_triggered == 0 and len(events[frame_id - 1]) > 0 and total_diff == 0: score += 10

                            if cc:
                                print(f'{n_triggered} rule triggered -> {[r for i_r, r in enumerate(obj.rules) if triggered_rules[i_r]]}')
                                print(f'from {sequence[-1]} to {e}')
                                if total_diff == 0:
                                    score += 10 * n_triggered
                                    print(f'cc != 0 and diff == 0 -> score + {10 * n_triggered}')
                                else:
                                    score -= 10 * n_triggered
                                    print(f'cc != 0 and diff != 0 -> score - {10 * n_triggered}')

                            if score > best_score:
                                best_score = score
                                best_idx = e_i

                        if n_triggered and cc == 0:
                            best_score -= 10 * n_triggered
                            print(f'n_triggered and cc == 0 -> score - {10 * n_triggered}')

                        sequence.append(frames[frame_id][best_idx])
                        current_others = frames[frame_id][:best_idx] + frames[frame_id][best_idx+1:]

                        object_score += best_score

                        # TODO: re-initialize properties or maintain the predicted ones (i expect a divergence in the second case)

                        for k, v in sequence[-1].properties.items(): properties[k] = v
                        #re-initializing k_dict means that the rules' coefficient work with property(i-1) instead of property(0)
                        k_dict = {Speed_x: Speed_x.compute(sequence[-2], sequence[-1], current_others), Speed_y: Speed_y.compute(sequence[-2], sequence[-1], current_others)}
                        properties[Speed_x] = k_dict[Speed_x]
                        properties[Speed_y] = k_dict[Speed_y]

                        events.append([])
                        for event in [Contact_With_Something_T, Contact_With_Something_B, Contact_With_Something_L, Contact_With_Something_R]:
                            if event.check(sequence[-2], sequence[-1], current_others): events[frame_id].append(event)

                    #print('sequence')
                    #print([e.id for e in sequence])
                    #print((total_difference, total_score))
                    #print('-------------------------------------------')
                            
                    if object_score > best_object_score:
                        best_object_score = object_score
                        best_sequence = sequence

                #print('best_sequence')

                all_the_same = True
                first = best_sequence[0].description
                for e in best_sequence:
                    if e.description != first:
                        all_the_same = False
                        break
                if all_the_same: print(f'all the sequence is {first}')
                else: print([e.description for e in best_sequence])
                
                #print(best_sequence)
                #print(f'best_total_score: {best_total_score}')

                individual_score += best_object_score

                for frame_id, e in enumerate(best_sequence):
                    if e.id in elements_usage[frame_id].keys(): elements_usage[frame_id][e.id].append(obj.id)
                    else: elements_usage[frame_id][e.id] = [obj.id]

            unique_element_frame_considered = 0
            element_frame_repetitions = 0
            for eu in elements_usage:
                unique_element_frame_considered += len(eu.keys())
                for _, objs_id_list in eu.items():
                    if len(objs_id_list) > 1: element_frame_repetitions += len(objs_id_list) - 1
            
            individual_score += unique_element_frame_considered
            print(f'unique_element_frame_considered: {unique_element_frame_considered}')

            individual_score -= element_frame_repetitions
            print(f'element_frame_repetitions: {element_frame_repetitions}')

            individual.fitness = individual_score
        
        #exit()

        #return scores
        return
    

if __name__ == '__main__':

    frames = load_elements_per_frame(None, ['pos_x', 'pos_y', 'hitbox_tl_x', 'hitbox_tl_y', 'hitbox_br_x', 'hitbox_br_y'])
    #for frame in frames:
    #    print(frame)
    #exit()
    debug_population = [
        Individual(0, ID_generator(), [
            Object(0, [
                Rule([Contact_With_Something_T], Speed_y, -2),
                Rule([Contact_With_Something_B], Speed_y, -2),
                Rule([Contact_With_Something_L], Speed_x, -2),
                Rule([Contact_With_Something_R], Speed_x, -2),
                ]),
            ]),

        Individual(1, ID_generator(), [
            Object(0, [
                Rule([Contact_With_Something_T], Speed_y, 2),
                Rule([Contact_With_Something_B], Speed_y, -2),
                Rule([Contact_With_Something_L], Speed_x, -2),
                Rule([Contact_With_Something_R], Speed_x, -2),
                ]),
            ]),

        Individual(2, ID_generator(), [
            Object(0, [
                Rule([Contact_With_Something_T], Speed_x, -2),
                Rule([Contact_With_Something_B], Speed_y, -2),
                Rule([Contact_With_Something_L], Speed_x, -2),
                Rule([Contact_With_Something_R], Speed_x, -2),
                ]),
            ]),

        Individual(3, ID_generator(), [
            Object(0, [
                Rule([Contact_With_Something_T], Speed_y, 2),
                Rule([Contact_With_Something_B], Speed_y, -2),
                Rule([Contact_With_Something_L], Speed_x, 2),
                Rule([Contact_With_Something_R], Speed_x, -2),
                ]),
            Object(1, [
                Rule([Contact_With_Something_T], Speed_y, 0),
                Rule([Contact_With_Something_B], Speed_y, 0),
                Rule([Contact_With_Something_L], Speed_x, 0),
                Rule([Contact_With_Something_R], Speed_x, 0),
                ]),
            ]),

        Individual(4, ID_generator(), [
            Object(0, [
                Rule([Contact_With_Something_T], Speed_y, 2),
                Rule([Contact_With_Something_B], Speed_y, -2),
                Rule([Contact_With_Something_L], Speed_x, 2),
                Rule([Contact_With_Something_R], Speed_x, -2),
                ]),
            Object(1, []),
            ]),

        Individual(5, ID_generator(), [
            Object(0, [
                Rule([Contact_With_Something_T], Speed_y, -2),
                ]),
            ]),

        Individual(6, ID_generator(), [
            Object(0, [
                Rule([Contact_With_Something_T], Speed_y, -2),
                Rule([Contact_With_Something_B], Speed_y, -2),
                ]),
            ]),

        Individual(7, ID_generator(), [
            Object(0, [
                Rule([Contact_With_Something_T], Speed_y, -2),
                Rule([Contact_With_Something_B], Speed_y, -2),
                Rule([Contact_With_Something_L], Speed_x, -2),
                ]),
            ]),

        Individual(8, ID_generator(), [
            Object(0, []),
            ]),

        ]
    FitnessEvaluator.evaluate(debug_population, frames)
    for ind in debug_population:
        print('------------------------------')
        print(f'ind_{ind.id}:\n{ind}\n>> fitness: {ind.fitness}')
