

class FormingIndividual:

    def __init__(self, objects_id, events, unassigned_patches):
        self.objects_id = [ob_id for ob_id in objects_id]
        self.events = {k: [ev for ev in v] for k, v in events.items()}
        self.unassigned_patches = [up for up in unassigned_patches]

class Individual:

    def __init__(self, object_dict, events, last_frame_id):

        self.object_dict = {obj_id: obj for obj_id, obj in object_dict.items()}

        self.object_info = {}
        for obj_id, current_obj in object_dict.items():
            frame_dict = {}
            for frame_id in range(0, last_frame_id):
                if frame_id in current_obj.frames_id:
                    frame_dict[frame_id] = {'present': True, 'unexplained': current_obj.unexplained[frame_id] if frame_id in current_obj.unexplained.keys() else [], 'events': events[(frame_id, obj_id)] if (frame_id, obj_id) in events.keys() else [], 'patch': object_dict[obj_id].sequence[object_dict[obj_id].frames_id.index(frame_id)]}
                else:
                    frame_dict[frame_id] = {'present': False, 'unexplained': current_obj.unexplained[frame_id] if frame_id in current_obj.unexplained.keys() else [], 'events': events[(frame_id, obj_id)] if (frame_id, obj_id) in events.keys() else [], 'patch': None}
            self.object_info[obj_id] = frame_dict

    def objects_id(self): return self.object_dict.keys()