import random
from evolutionary.individual import Individual


def mutate(population, population_size, id_generator, event_pool, property_pool, coefficient_pool):

    new_population = []

    # Mutation logic
    for individual in population:
        # Create a copy of the object to mutate
        new_ind = Individual(id= id_generator(), objects= individual.objects) #TODO check deepcopying, done in Individual.__init__

        mutate_what = ['add_obj', 'remove_obj', 'add_rule', 'remove_rule', 'modify_rule']
        mutate_what = random.choice(mutate_what)

        match mutate_what:
            case 'add_obj':
                pass
            case 'remove_obj':
                pass
            case 'add_rule':
                pass
            case 'remove_rule':
                pass
            case 'add_rule_trigger':
                pass
            case 'remove_rule_trigger':
                pass
            case 'modify_rule_equation':
                pass

    #TODO: Crossover (?)

    return new_population[:population_size]
