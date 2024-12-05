import itertools

from core.realization import Realization


class FitnessEvaluator:
    @staticmethod
    def evaluate(population, frames): #TODO: improve fitness after prototype running

        scores = []

        for i, individual in enumerate(population):
            print(f'individual {i+1}/{len(population)}')
            total_score = 0

            # Generate sequences for the individual
            for realization in FitnessEvaluator.generate_sequences(frames, individual):

                sequence_length = realization.length()
                total_score += sequence_length
                if sequence_length == len(frames): total_score +=  len(frames)

            # Penalize individual and object complexity
            total_score -= len(individual.objects)
            for obj in individual.objects:
                if obj.rules: total_score -= len(obj.rules)
                else: total_score -= 10  # Malus for object having no rules

            #TODO: Penalize objects that are never used in any sequence

            #TODO: Penalize for not explained elements

            # Assign fitness
            individual.fitness = total_score
            scores.append((individual, total_score))

        return scores

    @staticmethod
    def generate_sequences(frames, individual):
        
        #TODO: finish, check and correct, especially yield
        
        #TODO: try to invert the check, all_combinations checked on all individual

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
