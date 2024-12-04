import os
import pickle

from core.element import Element

class ID_generator:

    def __init__(self):
        self.prev_id = -1

    def __call__(self) -> int:
        self.prev_id += 1
        return self.prev_id
    
def load_elements_per_frame(log_file_name= None):

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

            elem = Element(elem_props['id'], description, elem_props)
            elements.append(elem)

        elements_per_frame.append(elements)

    return elements_per_frame