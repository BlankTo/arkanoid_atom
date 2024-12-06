import itertools

from core.realization import Realization


class FitnessEvaluator:
    @staticmethod
    def evaluate(population, frames): #TODO: improve fitness after prototype running

        scores = []

        for i, individual in enumerate(population):
            print(f'individual {i+1}/{len(population)}')
            total_score = 0

            elements_usage = []

            # Generate sequences for the individual
            for realization in FitnessEvaluator.generate_sequences(frames, individual):

                #TODO give points only when there is an event (?)

                sequence_length = realization.length()
                total_score += sequence_length
                if sequence_length == len(frames) - 1: total_score +=  len(frames)

                for i, e in enumerate(realization.sequence):
                    if i < len(elements_usage):
                        if e.id in elements_usage[i].keys(): elements_usage[i][e.id].add(realization.reference_object.id)
                        else: elements_usage[i][e.id] = set([realization.reference_object.id])
                    else: elements_usage.append({e.id: set([realization.reference_object.id])})

            # Penalize individual and object complexity
            total_score -= len(individual.objects)
            for obj in individual.objects:
                if obj.rules: total_score -= len(obj.rules)
                else: total_score -= 10  # Malus for object having no rules

            #TODO: Penalize objects that are never used in any sequence

            # elements usage

            objs_id_used = set()

            for i in range(min(len(frames), len(elements_usage))):
                total_score -= (len(frames[i]) - len(elements_usage[i].keys())) * 10

                for objs_associated_to_elem in elements_usage[i].values():
                    if len(objs_associated_to_elem) > 1: total_score -= pow(len(objs_associated_to_elem), 2)
                    for obj_id in objs_associated_to_elem: objs_id_used.add(obj_id)

            for obj in individual.objects:
                if obj.id not in objs_id_used: total_score -= 10

            # Assign fitness
            individual.fitness = total_score
            scores.append((individual, total_score))

        return scores

    @staticmethod
    def generate_sequences(frames, individual):

        for i, obj in enumerate(individual.objects):
            #print(f'object {i}/{len(individual.objects)}')
            #print(obj)

            if len(obj.rules) > 0:
            
                possible_realizations = []
                for e0 in frames[0]: possible_realizations.append((Realization(obj, [e0]), 1))

                while possible_realizations:
                    
                    #print('--')
                    #for rr in possible_realizations: print(rr)
                    #print(len(possible_realizations))
                    #if len(possible_realizations) > 36: exit(0)

                    considered_realization, offset = possible_realizations.pop(0)

                    if offset == len(frames): yield considered_realization
                    elif len(frames[offset]) == 0: yield considered_realization
                    else:

                        #print(offset)

                        element_added = False

                        for e1_i, e1 in enumerate(frames[offset]):

                            new_realization = considered_realization.validate(e1, frames[offset][:e1_i] + frames[offset][e1_i+1:])
                            
                            if new_realization is not None:
                                possible_realizations.append((new_realization, offset + 1))
                                element_added = True

                        if not element_added: yield considered_realization
