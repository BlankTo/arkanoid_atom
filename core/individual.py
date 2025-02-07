

class Individual:

    def __init__(self, object_dict, last_frame_id):

        self.object_dict = {obj_id: obj for obj_id, obj in object_dict.items()}

        self.rules = {obj_id: obj.rules for obj_id, obj in object_dict.items()}

        self.object_info = {}
        for obj_id, current_obj in object_dict.items():
            frame_dict = {}
            for frame_id in range(0, last_frame_id):
                frame_dict[frame_id] = {
                    'present': bool(frame_id in current_obj.frames_id),
                    'unexplained': current_obj.unexplained[frame_id] if frame_id in current_obj.unexplained.keys() else [],
                    'explained_unexplained': current_obj.explained_unexplained[frame_id] if frame_id in current_obj.explained_unexplained.keys() else [],
                    'events': current_obj.events[frame_id] if frame_id in current_obj.events.keys() else [],
                    'global_events': current_obj.global_events[frame_id] if frame_id in current_obj.global_events.keys() else [],
                    'patch': object_dict[obj_id].sequence[object_dict[obj_id].frames_id.index(frame_id)]if frame_id in current_obj.frames_id else None,
                    }
            self.object_info[obj_id] = frame_dict