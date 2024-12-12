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

        scores = []

        for ind_i, individual in enumerate(population):

            print(f'individual {ind_i+1}/{len(population)}')

            if individual.fitness is not None: continue
            
            total_score = 0

            elements_usage = [{} for _ in range(len(frames))]

            #for obj in individual.objects:
            for i_o, obj in enumerate(individual.objects):
                #print(f'object {i_o+1}/{len(individual.objects)}: {obj}')

                best_total_difference = math.inf
                best_score = 0
                best_sequence = None

                for e0, (e1_i, e1) in itertools.product(frames[0], enumerate(frames[1])):

                    #if e0.description != 'ball' or e1.description != 'ball': continue

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

                    total_difference = 0
                    score = 0

                    for frame_id in range(2, len(frames) - 1):

                        properties_changes = {}
                        triggered_rules = []

                        #print('properties:')
                        #for kk, vv in properties.items():
                        #    print((kk.name(), vv))
                        #print('modified properties:')

                        for rule in obj.rules:

                            triggered, effects = rule.effects(events[frame_id - 1])
                            
                            triggered_rules.append(triggered)

                            #if triggered: print(f'{[rule.events]} triggered')

                            for property_class, coeff in effects.items():
                                #print((property_class.name(), coeff))
                                if property_class in properties_changes.keys(): properties_changes[property_class] += coeff
                                else: properties_changes[property_class] = coeff

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

                        best_difference = math.inf
                        best_idx = None

                        for e_i, e in enumerate(frames[frame_id]):

                            #if e.description != 'ball': continue

                            #from core.property import Pos_x, Pos_y
                            #print(sequence)
                            #print(f'{e} vs {(properties[Pos_x], properties[Pos_y])}')

                            difference = 0

                            for property_class, value in e.properties.items():

                                difference += abs(properties[property_class] - value)

                                if cc and abs(properties[property_class] - value) == 0: score += 100

                            if difference < best_difference:
                                best_difference = difference
                                best_idx = e_i

                            #print(f'diff: {difference}')

                        if len(events[frame_id - 1]) > 0 and len(properties_changes.keys()) > 0:

                            if best_difference == 0 and cc:
                                #print('correct prediction after event')
                                score += 100 #at least one event, for evaluation
                                score += sum(triggered_rules) * 10
                            else:
                                score -= sum(triggered_rules) * 10

                        sequence.append(frames[frame_id][best_idx])
                        current_others = frames[frame_id][:best_idx] + frames[frame_id][best_idx+1:]

                        total_difference += best_difference
                        
                        if len(events[frame_id - 1]) > 0: score -= best_difference #at least one event, for evaluation

                        #print(f'total_diff: {total_difference}')
                        #print(events_bring_changes)
                        #print(f'chosen sequence: {sequence}')
                        #if events_bring_changes: exit()
                        #print('----------------------------------------------')

                        # TODO: re-initialize properties or maintain the predicted ones (i expect a divergence in the second case)

                        properties = {k: v for k, v in sequence[-1].properties.items()}
                        k_dict = {Speed_x: Speed_x.compute(sequence[-2], sequence[-1], current_others), Speed_y: Speed_y.compute(sequence[-2], sequence[-1], current_others)}
                        properties[Speed_x] = k_dict[Speed_x]
                        properties[Speed_y] = k_dict[Speed_y]

                        events.append([])
                        for event in [Contact_With_Something_T, Contact_With_Something_B, Contact_With_Something_L, Contact_With_Something_R]:
                            if event.check(sequence[-2], sequence[-1], current_others): events[frame_id].append(event)
                            
                    if total_difference < best_total_difference:
                        best_total_difference = total_difference
                        best_sequence = sequence
                        best_score = score
                    elif total_difference == best_total_difference and score > best_score:
                        best_total_difference = total_difference
                        best_sequence = sequence
                        best_score = score


                print('best_sequence')
                print(best_sequence)
                print(f'total_difference: {total_difference}')

                total_score -= best_total_difference
                total_score += best_score

                frame_id = 0
                for e in best_sequence:
                    if e.id in elements_usage[frame_id].keys(): elements_usage[frame_id][e.id].append(obj.id)
                    else: elements_usage[frame_id][e.id] = [obj.id]

            for eu in elements_usage:
                total_score += len(eu.keys())
                #if len(eu.keys()) > 0: print(f'+{len(eu.keys())}')
                for e_id, objs_id_list in eu.items():
                    if len(objs_id_list) > 1:
                        total_score -= len(objs_id_list)
                        #print(f'-{len(objs_id_list)}')

            #scores.append((individual, total_score))
            individual.fitness = total_score
        
        #exit()

        #return scores
        return
    

if __name__ == '__main__':

    frames = load_elements_per_frame(None, ['pos_x', 'pos_y', 'hitbox_tl_x', 'hitbox_tl_y', 'hitbox_br_x', 'hitbox_br_y'])
    #for frame in frames:
    #    print(frame)
    #exit()
    debug_population = [
#        Individual(0, ID_generator(), [
#            Object(0, [
#                Rule([Contact_With_Something_T], Speed_y, -2),
#                Rule([Contact_With_Something_B], Speed_y, -2),
#                Rule([Contact_With_Something_L], Speed_x, -2),
#                Rule([Contact_With_Something_R], Speed_x, -2),
#                ]),
#            ]),

#        Individual(1, ID_generator(), [
#            Object(0, [
#                Rule([Contact_With_Something_T], Speed_y, 2),
#                Rule([Contact_With_Something_B], Speed_y, -2),
#                Rule([Contact_With_Something_L], Speed_x, -2),
#                Rule([Contact_With_Something_R], Speed_x, -2),
#                ]),
#            ]),

        Individual(2, ID_generator(), [
            Object(0, [
                Rule([Contact_With_Something_T], Speed_x, 2),
                Rule([Contact_With_Something_B], Speed_y, -2),
                Rule([Contact_With_Something_L], Speed_x, -2),
                Rule([Contact_With_Something_R], Speed_x, -2),
                ]),
            ]),

#        Individual(3, ID_generator(), [
#            Object(0, [
#                Rule([Contact_With_Something_T], Speed_y, 2),
#                Rule([Contact_With_Something_B], Speed_y, -2),
#                Rule([Contact_With_Something_L], Speed_x, 2),
#                Rule([Contact_With_Something_R], Speed_x, -2),
#                ]),
#            Object(1, [
#                Rule([Contact_With_Something_T], Speed_y, 0),
#                Rule([Contact_With_Something_B], Speed_y, 0),
#                Rule([Contact_With_Something_L], Speed_x, 0),
#                Rule([Contact_With_Something_R], Speed_x, 0),
#                ]),
#            ]),

#        Individual(4, ID_generator(), [
#            Object(0, [
#                Rule([Contact_With_Something_T], Speed_y, 2),
#                Rule([Contact_With_Something_B], Speed_y, -2),
#                Rule([Contact_With_Something_L], Speed_x, 2),
#                Rule([Contact_With_Something_R], Speed_x, -2),
#                ]),
#            Object(1, []),
#            ]),

        ]
    FitnessEvaluator.evaluate(debug_population, frames)
    for ind in debug_population:
        print(f'ind_{ind.id}:\n{ind}\n>> fitness: {ind.fitness}')
