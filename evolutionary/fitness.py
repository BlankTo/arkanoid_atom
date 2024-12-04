import itertools

from core.sequence_validator import SequenceValidator


class FitnessEvaluator:
    @staticmethod
    def evaluate(population, frames): #TODO: improve fitness after prototype running

        scores = []

        for individual in population:
            total_score = 0

            # Generate sequences for the individual
            for sequence in FitnessEvaluator.generate_sequences(frames, individual):

                sequence_length = len(sequence)
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
    def generate_sequences(frames, individual): #TODO: finish, check and correct, especially yield

        possible_sequences = [([e1, e2], 2) for e1, e2 in itertools.product(frames[0], frames[1]) if SequenceValidator.validate([e1, e2], individual)]

        while possible_sequences:

            considered_sequence, offset = possible_sequences.pop(0)

            if offset == len(frames): yield considered_sequence

            stop_sequence = True
            for e in frames[offset]:
                new_sequence = considered_sequence + [e]
                if SequenceValidator.validate(new_sequence, individual):
                    possible_sequences.append((new_sequence, offset + 1))
                    stop_sequence = False
            
            if stop_sequence:
                yield considered_sequence
