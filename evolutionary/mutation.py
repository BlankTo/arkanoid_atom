import random
from core.individual import Individual
from utils.various import ID_generator


def mutate_one(new_id, base_individual, event_pool, property_pool, coefficient_pool):

    #print(f'mutating ind_{base_individual.id} into ind_{new_id}')

    new_ind = Individual(id= new_id, object_id_generator= ID_generator(), objects= base_individual.objects) # Deepcopying done in Individual.__init__

    mutate_what = ['add_obj']

    if len(new_ind.objects) > 1: mutate_what.append('remove_obj')
    if len(new_ind.objects) > 0: mutate_what.append('add_rule')
    objects_with_more_than_one_rule = []
    rules_with_modifiable_trigger = []
    rules_with_more_than_one_trigger = []
    rules_with_less_then_n_events_triggers = []
    all_rules = []
    for obj in new_ind.objects:
        if len(obj.rules) > 1: objects_with_more_than_one_rule.append(obj)
        for rule in obj.rules:
            all_rules.append(rule)
            if len(rule.events) > 1: rules_with_more_than_one_trigger.append(rule)
            if len(rule.events) < len(event_pool): rules_with_less_then_n_events_triggers.append(rule)
            if len(rule.events) > 0 and len(rule.events) < len(event_pool) - 1: rules_with_modifiable_trigger.append(rule)

    if objects_with_more_than_one_rule: mutate_what.append('remove_rule')
    if rules_with_less_then_n_events_triggers: mutate_what.append('add_rule_trigger')
    if rules_with_modifiable_trigger: mutate_what.append('modify_rule_trigger')
    if rules_with_more_than_one_trigger: mutate_what.append('remove_rule_trigger')
    if all_rules:
        mutate_what.append('modify_rule_property_class')
        mutate_what.append('modify_rule_coefficient')

    mutate_what = random.choice(mutate_what)

    match mutate_what:
        case 'add_obj':
            new_ind.add_new_object(event_pool, property_pool, coefficient_pool)
        case 'remove_obj':
            new_ind.remove_object()
        case 'add_rule':
            random.choice(new_ind.objects).add_new_rule(event_pool, property_pool, coefficient_pool)
        case 'remove_rule':
            random.choice(objects_with_more_than_one_rule).remove_rule()
        case 'add_rule_trigger':
            random.choice(rules_with_less_then_n_events_triggers).add_trigger(event_pool)
        case 'modify_rule_trigger':
            random.choice(rules_with_modifiable_trigger).modify_trigger(event_pool)
        case 'remove_rule_trigger':
            random.choice(rules_with_more_than_one_trigger).remove_trigger()
        case 'modify_rule_property_class':
            random.choice(all_rules).modify_property_class(property_pool)
        case 'modify_rule_coefficient':
            random.choice(all_rules).modify_coefficient(coefficient_pool)

    return new_ind

def mutate(population, population_size, id_generator, event_pool, property_pool, coefficient_pool):

    new_population = []

    for individual in population:
        new_population.append(mutate_one(id_generator(), individual, event_pool, property_pool, coefficient_pool))

    new_population = [p for p in population] + new_population

    #TODO: Crossover (?)

    while len(new_population) < population_size:
        #new_population.append(mutate_one(id_generator(), random.choice(population), event_pool, property_pool, coefficient_pool))
        new_population.append(mutate_one(id_generator(), random.choice(new_population), event_pool, property_pool, coefficient_pool))

    return new_population
