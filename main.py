from utils import load_patches_per_frame
from euristic import euristic_initialization, summarize_into_prototypes
from utils import debug_patches_per_frame

import pickle

def main():

    simple_arkanoid_log_file_name = 'arkanoid_log_2025_02_05_12_11_28.pkl'
    complete_arkanoid_lose_log_file_name = 'arkanoid_log_2025_02_05_12_13_01.pkl'
    complete_arkanoid_win_log_file_name = 'arkanoid_log_2025_02_05_12_15_01.pkl'
    
    #patches_per_frame = load_patches_per_frame(None) # last log
    #patches_per_frame = debug_patches_per_frame
    #patches_per_frame = load_patches_per_frame(simple_arkanoid_log_file_name)
    #patches_per_frame = load_patches_per_frame(complete_arkanoid_lose_log_file_name)
    patches_per_frame = load_patches_per_frame(complete_arkanoid_win_log_file_name)

    #population = euristic_initialization(patches_per_frame, debug= True)
    population = euristic_initialization(patches_per_frame[:-10], debug= True)
    
    print('\n\n=====================================\neuristic_initialization end\n=====================================\n')

    scores = []
    for ind_id, (ind, score) in enumerate(population):
        scores.append((ind_id, ind, score))
    
    population = [(ind_id, ind, score) for ind_id, ind, score in sorted(scores, key= lambda x: x[2])]#[:1]

    out_string = ''
    for ind_id, ind, score in population:
        out_string += f'\n--------------\nind_{ind_id}:\n--------------'
        for obj_id in ind.object_dict.keys():
                out_string += f'\n\nobj_{obj_id}'
                if obj_id in ind.rules.keys():
                    out_string += f'\n\nrules: {ind.rules[obj_id]}\n'
                else:
                    out_string += '\n\nno rules\n'
                for frame_id, frame_dict in ind.object_info[obj_id].items():
                    if frame_dict['present']:
                        out_string += f'\nframe {frame_id} - patch: {frame_dict["patch"]}\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}'
                    else:
                        out_string += f'\nframe {frame_id} - patch not present\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}'
        out_string += f'\nscore: {score}'
    with open('log.txt', 'w') as f:
        f.write(out_string)
    print(f'n° individuals: {len(population)}')

    with open('best_population.pkl', 'wb') as f:
        pickle.dump({tup[0]: tup[1] for tup in population}, f)
    
    with open('best_individual.pkl', 'wb') as f:
        pickle.dump(population[0][1], f)

    summarize_into_prototypes(population[0][1])

    with open('best_population.pkl', 'rb') as f:
        population = euristic_initialization(patches_per_frame, resume_population= pickle.load(f), debug= True)
    
    print('\n\n=====================================\neuristic_initialization resume end\n=====================================\n')

    scores = []
    for ind_id, (ind, score) in enumerate(population):
        scores.append((ind_id, ind, score))
    
    population = [(ind_id, ind, score) for ind_id, ind, score in sorted(scores, key= lambda x: x[2])]#[:1]

    out_string = ''
    for ind_id, ind, score in population:
        out_string += f'\n--------------\nind_{ind_id}:\n--------------'
        for obj_id in ind.object_dict.keys():
                out_string += f'\n\nobj_{obj_id}'
                if obj_id in ind.rules.keys():
                    out_string += f'\n\nrules: {ind.rules[obj_id]}\n'
                else:
                    out_string += '\n\nno rules\n'
                for frame_id, frame_dict in ind.object_info[obj_id].items():
                    if frame_dict['present']:
                        out_string += f'\nframe {frame_id} - patch: {frame_dict["patch"]}\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}'
                    else:
                        out_string += f'\nframe {frame_id} - patch not present\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}'
        out_string += f'\nscore: {score}'
    with open('log_resume.txt', 'w') as f:
        f.write(out_string)
    print(f'n° individuals: {len(population)}')

    with open('best_population_resume.pkl', 'wb') as f:
        pickle.dump({tup[0]: tup[1] for tup in population}, f)
    
    with open('best_individual_resume.pkl', 'wb') as f:
        pickle.dump(population[0][1], f)

    summarize_into_prototypes(population[0][1])

    return

if __name__ == "__main__":
    main()
