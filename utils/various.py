import os
import pickle

from core.element import Element
from core.property import Pos_x, Pos_y, Hitbox_tl_x, Hitbox_tl_y, Hitbox_br_x, Hitbox_br_y

class ID_generator:

    def __init__(self):
        self.prev_id = -1

    def __call__(self) -> int:
        self.prev_id += 1
        return self.prev_id
    
property_dict = {
    'pos_x': Pos_x,
    'pos_y': Pos_y,
    'hitbox_tl_x': Hitbox_tl_x,
    'hitbox_tl_y': Hitbox_tl_y,
    'hitbox_br_x': Hitbox_br_x,
    'hitbox_br_y': Hitbox_br_y,
}
    
def load_elements_per_frame(log_file_name= None, properties_to_load= None, descriptions_to_exclude= ['environment']):

    if log_file_name is None: # use last saved
        log_files_name = os.listdir('logs/arkanoid_logs')
        if not log_files_name: raise Exception('no saved logs')
        log_file_name = sorted(log_files_name, reverse= True)[0]

    log_file_path = f'logs/arkanoid_logs/{log_file_name}'
    with open(log_file_path, 'rb') as log_file:
        log = pickle.load(log_file)
    print(f'{log_file_path} loaded')

    elements_per_frame = []
    for frame in log:

        elements = []
        for description, elem_props in frame['elements'].items():
            if description in descriptions_to_exclude: continue
            
            elements.append(Element(elem_props['id'], description, {property_dict[k]: v for k, v in elem_props.items() if k in properties_to_load}))

        elements_per_frame.append(elements)

    return elements_per_frame