from utils import load_patches_per_frame
from euristic import euristic_initialization

def main():
    
    ## Retrieve log and convert each patch in each frame to anonymous Patch objects

    log_file_name = None
    patches_per_frame = load_patches_per_frame(log_file_name)

    ## Definition of possible sequences and euristic population

    from core.patch import Patch
    from core.property import Pos_x, Pos_y, Shape_x, Shape_y

    debug_patches_per_frame_0 = [
        [ # frame 0
            Patch('ball', {
                Pos_x: 3,
                Pos_y: 1,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('wall', {
                Pos_x: 5,
                Pos_y: 3,
                Shape_x: 0,
                Shape_y: 2,
            }),
        ],
        [ # frame 1
            Patch('ball', {
                Pos_x: 4,
                Pos_y: 2,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('wall', {
                Pos_x: 5,
                Pos_y: 3,
                Shape_x: 0,
                Shape_y: 2,
            }),
        ],
        [ # frame 2
            Patch('ball', {
                Pos_x: 3,
                Pos_y: 3,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('wall', {
                Pos_x: 5,
                Pos_y: 3,
                Shape_x: 0,
                Shape_y: 2,
            }),
        ],
        [ # frame 2
            Patch('ball', {
                Pos_x: 2,
                Pos_y: 4,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('wall', {
                Pos_x: 5,
                Pos_y: 3,
                Shape_x: 0,
                Shape_y: 2,
            }),
        ],
    ]

    debug_patches_per_frame = [
        [ # frame 0
            Patch('ball_a', {
                Pos_x: 4,
                Pos_y: 3,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('ball_b', {
                Pos_x: 4,
                Pos_y: 1,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('wall_a', {
                Pos_x: 6,
                Pos_y: 2,
                Shape_x: 0,
                Shape_y: 1,
            }),
            Patch('wall_b', {
                Pos_x: 1,
                Pos_y: 2,
                Shape_x: 0,
                Shape_y: 1,
            }),
        ],
        [ # frame 1
            Patch('ball_a', {
                Pos_x: 3,
                Pos_y: 2,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('ball_b', {
                Pos_x: 5,
                Pos_y: 2,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('wall_a', {
                Pos_x: 6,
                Pos_y: 2,
                Shape_x: 0,
                Shape_y: 1,
            }),
            Patch('wall_b', {
                Pos_x: 1,
                Pos_y: 2,
                Shape_x: 0,
                Shape_y: 1,
            }),
        ],
        [ # frame 2
            Patch('ball_a', {
                Pos_x: 2,
                Pos_y: 1,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('ball_b', {
                Pos_x: 4,
                Pos_y: 3,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('wall_a', {
                Pos_x: 6,
                Pos_y: 2,
                Shape_x: 0,
                Shape_y: 1,
            }),
            Patch('wall_b', {
                Pos_x: 1,
                Pos_y: 2,
                Shape_x: 0,
                Shape_y: 1,
            }),
        ],
        [ # frame 3
            Patch('ball_a', {
                Pos_x: 3,
                Pos_y: 0,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('ball_b', {
                Pos_x: 3,
                Pos_y: 4,
                Shape_x: 0,
                Shape_y: 0,
            }),
            Patch('wall_a', {
                Pos_x: 6,
                Pos_y: 2,
                Shape_x: 0,
                Shape_y: 1,
            }),
        ],
    ]
    population = euristic_initialization(debug_patches_per_frame, debug= True)
    #population = euristic_initialization(patches_per_frame[:100])
    
    print('\n\n=====================================\ndebug_end\n=====================================\n')

    scores = []
    for ind_id, ind in enumerate(population):
        score = 0
        for obj_id in ind.object_dict.keys():
            for frame_dict in ind.object_info[obj_id].values():
                score += len(frame_dict['unexplained'])
        scores.append((ind_id, ind, score))
    
    population = [(ind_id, ind, score) for ind_id, ind, score in sorted(scores, key= lambda x: x[2], reverse= True)]

    out_string = ''

    for ind_id, ind, score in population:
        
        ok = False
        for obj_id in ind.object_dict.keys():
            if obj_id in ind.rules.keys(): ok = True
        if not ok: continue

        print(f'\n--------------\nind_{ind_id}:\n--------------')
        out_string += f'\n--------------\nind_{ind_id}:\n--------------'

        for obj_id in ind.object_dict.keys():
                print(f'\nobj_{obj_id}')
                out_string += f'\n\nobj_{obj_id}'

                if obj_id in ind.rules.keys():
                    print(f'\nrules: {ind.rules[obj_id]}\n')
                    out_string += f'\n\nrules: {ind.rules[obj_id]}\n'
                else:
                    print('\nno rules\n')
                    out_strig += '\n\nno rules\n'

                for frame_id, frame_dict in ind.object_info[obj_id].items():
                    if frame_dict['present']:
                        print(f'frame {frame_id} - patch: {frame_dict["patch"]}\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}')
                        out_string += f'\nframe {frame_id} - patch: {frame_dict["patch"]}\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}'
                    else:
                        print(f'frame {frame_id} - patch not present\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}')
                        out_string += f'\nframe {frame_id} - patch not present\n- unexplained: {frame_dict["unexplained"]}\n- explained: {frame_dict["explained_unexplained"]}\n- events: {frame_dict["events"]}'

        print(f'score: {score}')
        out_string += f'\nscore: {score}'

    with open('log.txt', 'w') as f:
        f.write(out_string)

    return

    initial_population = euristic_initialization(patches_per_frame)

    # evolutionary algorithm



    # Output results



    return

if __name__ == "__main__":
    main()
