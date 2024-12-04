class SequenceValidator:

    @staticmethod
    def validate_obj(sequence, obj):
        k_values = set()
        for i in range(len(sequence) - 1):
            element1 = sequence[i]
            element2 = sequence[i + 1]
            for rule in obj.rules:
                possible_k = rule.validate(element1, element2)
                if possible_k == 'no': return False
                elif possible_k == 'all_k': continue
                else:
                    if k_values:
                        k_values = k_values & possible_k
                        if not k_values: return False
                    else: k_values = possible_k

        return bool(k_values)
    
    @staticmethod
    def validate(sequence, individual):
        for obj in individual.objects:
            if SequenceValidator.validate_obj(sequence, obj): return True # at least one object explain the sequence
        
        return False
    

#TODO: modify sequence in realization and keep in its memory the previously computed k to speed up computation