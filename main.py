from utils import load_patches_per_frame
from euristic import euristic_initialization
from utils import debug_patches_per_frame

def main():
    
    ## Retrieve log and convert each patch in each frame to anonymous Patch objects

    log_file_name = None
    patches_per_frame = load_patches_per_frame(log_file_name)

    #population = euristic_initialization(debug_patches_per_frame, debug= True)
    population = euristic_initialization(debug_patches_per_frame[:14], debug= True)
    #population = euristic_initialization(debug_patches_per_frame)
    #population = euristic_initialization(patches_per_frame[:100])
    #population = euristic_initialization(patches_per_frame[:100], debug= True)
    
    print('\n\n=====================================\ndebug_end\n=====================================\n')
    #exit()

    scores = []
    for ind_id, (ind, score) in enumerate(population):
        scores.append((ind_id, ind, score))
    
    population = [(ind_id, ind, score) for ind_id, ind, score in sorted(scores, key= lambda x: x[2])][:1]

    out_string = ''

    for ind_id, ind, score in population:
        
        ok = False
        for obj_id in ind.object_dict.keys():
            if obj_id in ind.rules.keys(): ok = True
        if not ok: continue

        #print(f'\n--------------\nind_{ind_id}:\n--------------')
        out_string += f'\n--------------\nind_{ind_id}:\n--------------'

        for obj_id in ind.object_dict.keys():
                #print(f'\nobj_{obj_id}')
                out_string += f'\n\nobj_{obj_id}'

                if obj_id in ind.rules.keys():
                    #print(f'\nrules: {ind.rules[obj_id]}\n')
                    out_string += f'\n\nrules: {ind.rules[obj_id]}\n'
                else:
                    #print('\nno rules\n')
                    out_string += '\n\nno rules\n'

                for frame_id, frame_dict in ind.object_info[obj_id].items():
                    if frame_dict['present']:
                        #print(f'frame {frame_id} - patch: {frame_dict["patch"]}\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}')
                        out_string += f'\nframe {frame_id} - patch: {frame_dict["patch"]}\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}'
                    else:
                        #print(f'frame {frame_id} - patch not present\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}')
                        out_string += f'\nframe {frame_id} - patch not present\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}'

        #print(f'score: {score}')
        out_string += f'\nscore: {score}'

    with open('log.txt', 'w') as f:
        f.write(out_string)

    print(f'n° individuals: {len(population)}')

    return

    initial_population = euristic_initialization(patches_per_frame)

    # evolutionary algorithm



    # Output results



    return

if __name__ == "__main__":
    main()
