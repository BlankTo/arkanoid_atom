from core.individual import Individual
from evolutionary.fitness import FitnessEvaluator
from evolutionary.mutation import mutate
from core.events import (
    Contact_With_Something_T,
    Contact_With_Something_B,
    Contact_With_Something_L,
    Contact_With_Something_R,
)
from core.property import (
    Speed_x,
    Speed_y,
)
from utils.various import ID_generator

class EvolutionaryAlgorithm:
    def __init__(self, frames, population_size= 100, max_generations= 100, survival_rate= 0.2):
       
        self.frames = frames
        self.population_size = population_size
        self.max_generations = max_generations
        self.survival_rate= survival_rate
        self.individual_id_generator = ID_generator()

        self.event_pool = [
            Contact_With_Something_T(),
            Contact_With_Something_B(),
            Contact_With_Something_L(),
            Contact_With_Something_R(),
        ]
        self.property_pool = [Speed_x, Speed_y]
        self.coefficient_pool = [-2, -1, 1, 2]

        self.initialize_population()

    def initialize_population(self):

        self.population = [Individual(id= self.individual_id_generator(), object_id_generator= ID_generator()).initialize(self.event_pool, self.property_pool, self.coefficient_pool) for _ in range(self.population_size)]

        #for ind in self.population:
        #    print(f'individual_{ind.id}:\n{ind}')
        #exit()

    def run(self):
        
        for generation in range(self.max_generations):
            # Evaluation

            #fitness_scores = FitnessEvaluator.evaluate(self.population, self.frames)
            #self.population = [individual for individual, _ in sorted(fitness_scores, key=lambda x: x[1], reverse=True)]
            FitnessEvaluator.evaluate(self.population, self.frames)
            self.population = [individual for individual in sorted(self.population, key=lambda x: x.fitness, reverse=True)]

            # Selection
            survivors = self.population[: int(self.population_size * self.survival_rate)]
            
            #for ss in survivors:
            #    print(f'ind_{ss.id}: {ss} - score: {ss.fitness}')
            #exit()

            # Reproduction
            self.population = mutate(survivors, self.population_size, self.individual_id_generator, self.event_pool, self.property_pool, self.coefficient_pool)

            #print('--------------------------------\n--------------------------------')
            #for ind in self.population:
            #    print(f'ind_{ind.id}: {ind} - score: {ind.fitness}')
            #exit()

            # Log
            best_individual = survivors[0]
            print(f"----------------------------\nGeneration {generation}/{self.max_generations}\n Best individual:\n{best_individual}\nwith fitness: {best_individual.fitness}")

        # Return the best individuals
        return self.population[:10]
