from utils.various import load_elements_per_frame
from core.element import Element
from evolutionary.algorithm import EvolutionaryAlgorithm

def main():
    # Step 1: Retrieve log

    log_file_name = None
    #log_file_name = 'arkanoid_log_2024_12_02_12_18_40.pkl'
    elements_per_frame = load_elements_per_frame(log_file_name, ['pos_x', 'pos_y', 'hitbox_tl_x', 'hitbox_tl_y', 'hitbox_br_x', 'hitbox_br_y'])

    # Step 2: Initialize the evolutionary algorithm
    ea = EvolutionaryAlgorithm(elements_per_frame)

    # Step 3: Run the evolutionary algorithm
    best_individuals = ea.run()

    # Step 4: Output results
    print('best_individual:')
    for obj in best_individuals[0].objects:
        print(obj)

if __name__ == "__main__":
    main()
